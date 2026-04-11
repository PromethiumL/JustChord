import threading
import time

import rtmidi as rt
from PyQt6.QtCore import QThread, pyqtSignal

from JustChord.core import chord

DEFAULT_MIDI_IN_PORT = 0
MIDI_INITIALIZED = False
CHECK_INTERVAL_MS = 10

# MIDI protocol constants
MIDI_NOTE_ON = 0x90
MIDI_NOTE_OFF = 0x80
MIDI_CC = 0xB0
MIDI_CC_SUSTAIN_PEDAL = 64
MIDI_SUSTAIN_THRESHOLD = 64
MIDI_MIDDLE_C = 60

sustainPedalDown = False
pressedNotes = set()
sustainedNotes = set()
currentChords = []
midiIn = rt.MidiIn()


class KeyDetector:
    WINDOW_SIZE = 16
    DEFAULT_KEY = "C"
    RELATED_KEYS = {
        0: ["Db", "Ab", "Eb", "Bb", "F", "C", "G"],
        5: ["Gb", "Db", "Ab", "Eb", "Bb", "F", "C"],
        10: ["B", "Gb", "Db", "Ab", "Eb", "Bb", "F"],
        3: ["E", "B", "Gb", "Db", "Ab", "Eb", "Bb"],
        8: ["A", "E", "B", "Gb", "Db", "Ab", "Eb"],
        1: ["D", "A", "E", "B", "Gb", "Db", "Ab"],
        6: ["G", "D", "A", "E", "B", "Gb", "Db"],
        11: ["C", "G", "D", "A", "E", "B", "Gb"],
        4: ["F", "C", "G", "D", "A", "E", "B"],
        9: ["Bb", "F", "C", "G", "D", "A", "E"],
        2: ["Eb", "Bb", "F", "C", "G", "D", "A"],
        7: ["Ab", "Eb", "Bb", "F", "C", "G", "D"],
    }
    frequencyDict = {}
    currentKey = "C"

    def __init__(self):
        self.noteWindow = []
        for keyName in "C,F,Bb,Eb,Ab,Db,Gb,B,E,A,D,G".split(","):
            self.frequencyDict[keyName] = 0

    def addNote(self, pitch):
        weight = 1 if pitch > MIDI_MIDDLE_C else 2
        pitch %= 12
        if len(self.noteWindow) >= self.WINDOW_SIZE:
            for keyName in self.RELATED_KEYS[self.noteWindow[0][0]]:
                self.frequencyDict[keyName] -= self.noteWindow[0][1]
            self.noteWindow.pop(0)
        for keyName in self.RELATED_KEYS[pitch]:
            self.frequencyDict[keyName] += weight
        self.noteWindow.append((pitch, weight, self.currentKey))
        result = list(reversed(sorted(self.frequencyDict.items(), key=lambda i: self.frequencyDict[i[0]])))
        if len(result) == 0:
            KeyDetector.currentKey = self.DEFAULT_KEY
            return
        KeyDetector.currentKey = result[0][0]


def initRtMidi(port=DEFAULT_MIDI_IN_PORT):
    global midiIn, MIDI_INITIALIZED
    midiIn.close_port()
    midiIn = rt.MidiIn()
    portCount = midiIn.get_port_count()

    if port is None or port >= portCount:
        return

    if portCount:
        midiIn.open_port(port)
        MIDI_INITIALIZED = True
    else:
        raise Exception("No MIDI IN port found.")


class Monitor(QThread):
    trigger = pyqtSignal(str)
    keyDetector = KeyDetector()

    def __init__(self):
        super().__init__()
        self.msg_queue = []
        self.lock = threading.RLock()

    def run(self):
        global midiIn
        while True:
            if self.msg_queue:
                self.process_queue()
            if not midiIn.is_port_open():
                time.sleep(CHECK_INTERVAL_MS * 0.001)
                continue
            msg = midiIn.get_message()
            if msg:
                msg = msg[0]  # the raw data
                if len(msg) < 3:
                    continue
                self.msg_queue.append(msg)
            else:
                time.sleep(CHECK_INTERVAL_MS * 0.001)

    def process_queue(self):
        while self.msg_queue:
            with self.lock:
                self.process_message(self.msg_queue.pop(0))
        global pressedNotes
        self.update(list(pressedNotes | sustainedNotes))

    def append_message(self, msg):
        with self.lock:
            self.msg_queue.append(msg)

    def process_message(self, msg):
        global sustainPedalDown, pressedNotes, sustainedNotes
        channel = msg[0]
        pitch = msg[1]
        velocity = msg[2]

        # Normalize to strip MIDI channel number (process all 16 channels)
        channel = channel >> 4 << 4
        if channel == MIDI_CC and pitch == MIDI_CC_SUSTAIN_PEDAL:
            if velocity >= MIDI_SUSTAIN_THRESHOLD:
                sustainPedalDown = True
            else:
                sustainPedalDown = False
                sustainedNotes = set()
            return

        if velocity > 0 and channel == MIDI_NOTE_ON:
            pressedNotes.add(pitch)
            self.keyDetector.addNote(pitch)
        elif channel == MIDI_NOTE_OFF or channel == MIDI_NOTE_ON:
            if sustainPedalDown:
                if pitch in pressedNotes:
                    sustainedNotes.add(pitch)
                    pressedNotes.discard(pitch)
            else:
                pressedNotes.discard(pitch)

    def update(self, notes):
        global currentChords
        if notes:
            chord_list = chord.identifyChord(notes)
            currentChords = chord_list
            if len(list(filter(lambda c: not c.isBlank, chord_list))) == 0:
                root = chord.getPitchName(min(notes))
                currentChords.append(chord.Chord(root, [], root, blankChord=True))
        self.trigger.emit("update")

    @property
    def midiIn(self):
        global midiIn
        return midiIn


monitor: Monitor
if __name__ != "__main__":
    monitor = Monitor()
