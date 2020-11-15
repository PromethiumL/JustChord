import rtmidi as rt
import time

from PyQt5.QtCore import *

import sys
import os

from JustChord.core import chord

DEFAULT_MIDI_IN_PORT = 0
MIDI_INITIALIZED = False
CHECK_INTERVAL_MS = 10

sustainPedalDown = False
pressedNotes = set()
sustainedNotes = set()
currentChords = []
midiIn = rt.MidiIn()

class KeyDetector:
    WINDOW_SIZE = 16
    DEFAULT_KEY = 'C'
    RELATED_KEYS = {
        0: ['Db', 'Ab', 'Eb', 'Bb', 'F', 'C', 'G'],
        5: ['Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F', 'C'],
        10: ['B', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F'],
        3: ['E', 'B', 'Gb', 'Db', 'Ab', 'Eb', 'Bb'],
        8: ['A', 'E', 'B', 'Gb', 'Db', 'Ab', 'Eb'],
        1: ['D', 'A', 'E', 'B', 'Gb', 'Db', 'Ab'],
        6: ['G', 'D', 'A', 'E', 'B', 'Gb', 'Db'],
        11: ['C', 'G', 'D', 'A', 'E', 'B', 'Gb'],
        4: ['F', 'C', 'G', 'D', 'A', 'E', 'B'],
        9: ['Bb', 'F', 'C', 'G', 'D', 'A', 'E'],
        2: ['Eb', 'Bb', 'F', 'C', 'G', 'D', 'A'],
        7: ['Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D']
    }
    frequencyDict = {}
    currentKey = 'C'

    def __init__(self):
        self.noteWindow = []
        for keyName in "C,F,Bb,Eb,Ab,Db,Gb,B,E,A,D,G".split(','):
            self.frequencyDict[keyName] = 0

    def addNote(self, pitch):
        weight = 1 if pitch > 60 else 2
        pitch %= 12
        if len(self.noteWindow) >= self.WINDOW_SIZE:
            for keyName in self.RELATED_KEYS[self.noteWindow[0][0]]:
                self.frequencyDict[keyName] -= self.noteWindow[0][1]  # + (1 if self.noteWindow[0][2] == keyName else 0)
            self.noteWindow.pop(0)
        for keyName in self.RELATED_KEYS[pitch]:
            self.frequencyDict[keyName] += weight  # + (1 if self.currentKey == keyName else 0)
        self.noteWindow.append((pitch, weight, self.currentKey))
        result = list(reversed(sorted(self.frequencyDict.items(), key=lambda i: self.frequencyDict[i[0]])))
        # print(result)
        if len(result) == 0:
            KeyDetector.currentKey = self.DEFAULT_KEY
            return
        KeyDetector.currentKey = result[0][0]


def initRtMidi(port=DEFAULT_MIDI_IN_PORT):
    global midiIn
    # midiin = rt.RtMidiIn()
    midiIn = rt.MidiIn()
    # portCount = midiin.getPortCount()
    portCount = midiIn.get_port_count()

    if port >= portCount:
        print(f'port {port} is invalid. Fallback to default port.')
        port = 0

    if portCount:
        # midiin.openPort(port)
        midiIn.open_port(port)
        print('started monitoring MIDI input... port {}'.format(port))
        global MIDI_INITIALIZED
        MIDI_INITIALIZED = True
    else:
        raise Exception("No MIDI IN port found.")


class Monitor(QThread):
    trigger = pyqtSignal(str)
    keyDetector = KeyDetector()

    def __init__(self):
        super(Monitor, self).__init__()
        self.msg_queue = []

    def run(self):
        global midiIn
        while True:
            # msg = midiin.getMessage()
            msg = midiIn.get_message()
            if msg:
                msg = msg[0]  # the raw data
                if len(msg) < 3:
                    continue
                self.msg_queue.append(msg)
            else:
                if self.msg_queue:
                    self.process_queue()
                time.sleep(CHECK_INTERVAL_MS * 0.001)

    def process_queue(self):
        while self.msg_queue:
            self.process_message(self.msg_queue.pop(0))
        global pressedNotes
        self.update(list(pressedNotes | sustainedNotes))

    def process_message(self, msg):
        global sustainPedalDown
        global pressedNotes
        global sustainedNotes
        c = msg[0]  # channel
        p = msg[1]  # pitch
        v = msg[2]  # velocity
        # print(msg)
        # check the pedal cc [0xB0, 64, velo]

        # Currently, it's better to process all 16 channels.
        c = c >> 4 << 4  # remove this line for only channel 1.
        if c == 0xB0 and p == 64:
            if v >= 64:
                sustainPedalDown = True
            else:
                sustainPedalDown = False
                sustainedNotes = set()
            # if len(pressedNotes | sustainedNotes) >= 0:  # keep updating
            # self.update(list(pressedNotes | sustainedNotes))
            return

        # update note status
        if v > 0 and c != 0x80:
            if c == 0x90:
                pressedNotes.add(p)
                self.keyDetector.addNote(p)
                # print(self.keyDetector.currentKey)
        elif c == 0x80 or c == 0x90:  # "note off" or "note on, velocity=0"
            if sustainPedalDown:
                if p in pressedNotes:
                    sustainedNotes.add(p)
                    pressedNotes.discard(p)
            else:
                pressedNotes.discard(p)

    def update(self, notes):
        global currentChords
        global ALLOW_SLASH_CHORD
        if notes:
            l = chord.identifyChord(notes)
            currentChords = l
            if len(list(filter(lambda c: c.isBlank == False, l))) == 0:
                root = chord.getPitchName(min(notes))
                currentChords.append(chord.Chord(root, [], root, blankChord=True))
        # else:
        # print(''.join(s + ' ' for s in l[0].noteNames))
        self.trigger.emit('update')


if __name__ == '__monitor__':
    print('loading monitor..')
