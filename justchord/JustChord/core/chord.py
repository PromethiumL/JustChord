import re
import copy

from .constants import *


# def bp():
#     pdb.set_trace()

def getPitchNumber(name):
    """returns the midi pitch number of the given noteName"""
    result = re.match(r'[A-G](b{1,2}|x|#|\*|n)?', name)
    if not result:
        raise 'Invalid note name: {}'.format(name)
    result = result.group(0)
    # print(result)
    pitchName = result.replace('n', '')
    octave = name[len(pitchName):]
    # print('octave = ', octave)
    if not octave:
        octave = 4
    try:
        i = PITCH_INDEX[pitchName]  # pitch index
        result = (int(octave) + 1) * 12 + i
    except Exception as e:
        raise e
    return result


def getPitchName(pitch, key=DEFAULT_KEY, roman_style=USE_ROMAN_STYLE, with_octave=False, specified_letter=""):
    """specified_letter will not work when roman_style == True"""

    p = pitch % 12
    accidentalNumber = getAccidentalNumber(key)
    offset = 0

    if specified_letter in {'C', 'D', 'E', 'F', 'G', 'A', 'B'} and not roman_style:
        candidates = list(filter(lambda s: s[0] == specified_letter, list(PITCH_INDEX)))
        if candidates == []:
            result = getPitchName(pitch, with_octave=True)
            print('Enharmonically subsituted: {}'.format(result))
            return result
            # raise Exception("Incorrect Note: letter {} does not match any note".format(specified_letter))
        for s in candidates:
            if PITCH_INDEX[s] % 12 == p:
                letter = s
                octave = ""
                if with_octave:
                    octave = getPitchOctaveNumber(pitch)
                    if PITCH_INDEX[s] > 12:
                        octave += 1
                    if PITCH_INDEX[s] < 0:
                        octave -= 1
                    octave = str(octave)
                return letter + octave

    if roman_style:
        offset += 2  # use roman numerals
        p += 12 - accidentalNumber

    octaveInfo = str(getPitchOctaveNumber(pitch)) if with_octave else ""

    if key in KEY_LIST[0]:  # if it's a sharp key
        return DEGREE_NAMES[offset][p] + octaveInfo
    else:
        return DEGREE_NAMES[1 + offset][p] + octaveInfo


def addIntervalToNoteName(name, interval):
    if interval not in globals():
        raise Exception("Incorrect interval: {}".format(interval))

    pitch = getPitchNumber(name)
    letter = name[0]
    octave = ''.join(list(filter(lambda x: ord('0') <= ord(x) <= ord('9'), list(name))))
    # print("name: {}".format(octave))
    newPitch = pitch + eval(interval)
    letterShift = int(interval[1:]) - 1
    newLetter = "ABCDEFG"[("ABCDEFG".index(letter) + letterShift) % 7]
    return getPitchName(newPitch, with_octave=(octave != ''), specified_letter=newLetter)


def getPitchOctaveNumber(pitch):
    return pitch // 12 - 1


def getKeyName(i, sharp=False):
    if i == 0:
        return 'C'
    else:
        return KEY_LIST[0 if sharp else 1][i - 1]


def getAccidentalNumber(keyName):
    if keyName in KEY_LIST[0]:
        return KEY_LIST[0].index(keyName) + 1
    elif keyName in KEY_LIST[1]:
        return KEY_LIST[1].index(keyName) + 1
    else:
        return 0


def getInterval(pitch1, pitch2):
    """calc Interval smaller than an octave from given pitches"""
    if pitch1 <= pitch2:
        pitch2 -= (pitch2 - pitch1) // 12 * 12
    else:
        pitch2 += ((pitch1 - pitch2) // 12 + 1) * 12
    return pitch2 - pitch1


def identifyChord(noteList, key=DEFAULT_KEY, roman_style=USE_ROMAN_STYLE):
    """Ensure that the 'noteList' is non-empty"""
    if not noteList:
        raise Exception("'identifyChord' received an empty noteList")
    results = []
    notes = sorted(noteList)
    # get the actual bass (lowest) note
    lowestNote = notes[0] % 12

    # get the pitch set
    notes = sorted(list(set(map(lambda x: x % 12, notes))))
    for root in notes:
        intervals = set(map(lambda x: getInterval(root, x), notes))
        chord = Chord(root, intervals, lowestNote)
        if chord.recognized:
            # print(chord.name)
            if root == lowestNote:
                chord.complexity -= 3
            results.append(chord)
    results.sort(key=lambda c: c.complexity)
    return results


def identifyChordName(noteArray, key=DEFAULT_KEY, roman_style=USE_ROMAN_STYLE):
    return map(lambda x: x.name, identifyChord(noteArray, key=key, roman_style=roman_style))


# def getChordIntervalName(rootNote, )

class Chord:
    def __init__(self, rootName, intervals=None, bassName=None, chordType=None, blankChord=False):
        if bassName is None:
            bassName = rootName
        self.setRoot(rootName)
        self.setBass(bassName)
        self.name = ''
        self.chordTypes = []
        self.intervals = intervals
        self.intervalNames = set()
        self.notes = set()
        self.noteNames = set()
        self.isBlank = blankChord or intervals == {0} or intervals == set()
        if chordType is not None:
            if self.parseChordType(chordType):
                return
            else:
                raise Exception("Unrecognized chordName '{}'".format(chordType))
        self.recognized = False
        self.complexity = 0
        if not blankChord:
            self.updateName()

    def setRoot(self, rootName):
        if type(rootName) is int:
            self.rootName = getPitchName(rootName)
            self.rootPitch = rootName
        else:
            self.rootName = rootName
            self.rootPitch = PITCH_INDEX[self.rootName]

    def setBass(self, bassName):
        if type(bassName) is int:
            self.bassName = getPitchName(bassName)
            self.bassPitch = bassName
        else:
            self.bassName = bassName
            self.bassPitch = PITCH_INDEX[self.bassName]

    def buildChord(self):
        self.chordType = ''
        self.complexity = 0
        self.recognized = False
        s = set()
        for item in CHORD_DATA:
            # print('{} vs {}'.format(self.intervals, set(map(lambda intervalName:eval(intervalName), item[0]))))
            if self.intervals == set(map(lambda intervalName: (eval(intervalName) % 12), item[0])):
                self.recognized = True
                self.intervalNames = item[0]
                s.add((item[2], item[1]))
                break
                # comment 'break' for more possible results.
        if self.recognized:
            l = sorted(list(s))
            self.chordType = l[0][1]
            if self.bassName.upper() != self.rootName.upper():
                self.complexity += 1
                # Inversion increases the complexity.
        else:
            self.chordType = None
            # 'recognized' remains False.

        self.notes = set(map(
            lambda x: (x + PITCH_INDEX[self.rootName] % 12),
            list(self.intervals)
        ))

    def updateName(self, key=DEFAULT_KEY, roman_style=USE_ROMAN_STYLE):
        if not self.recognized:
            self.buildChord()
        self.rootName = getPitchName(self.rootPitch, key, roman_style)
        self.bassName = getPitchName(self.bassPitch, key, roman_style)
        self.typeName = self.chordType
        self.spellNoteNames()
        if roman_style and self.typeName is not None:
            if self.isMinorChord():
                self.rootName = self.rootName.lower()  # E.g. 'III' -> 'iii'
                self.bassName = self.bassName.lower()
                if self.typeName[0] == 'm':
                    self.typeName = self.typeName[1:]
                if self.typeName[0:3] == 'dim':
                    self.typeName = '°' + self.typeName[3:]
        elif self.typeName is None:
            self.typeName = 'n.c.'
        self.name = (
            self.rootName, self.typeName + (' / ' + self.bassName if self.rootName != self.bassName else '')
        )

    def parseChordType(self, chordType):
        chordType.replace(' ', '')
        for intervals, name, complexity in CHORD_DATA:
            if name == chordType:
                self.complexity = complexity
                self.intervals = intervals
                self.notes = list(
                    map(lambda x: (x + self.rootPitch) % 12, list(intervals)))
                self.chordType = chordType
                return True
        return False

    def isInterval(self):
        return len(self.intervals) == 2 and self.intervals != set([U1, P5])

    def isMinorChord(self):
        return M3 not in self.intervals and m3 in self.intervals

    def getBaseName(self, key=DEFAULT_KEY, roman_style=USE_ROMAN_STYLE):
        return getPitchName(self.rootPitch) + ' ' + self.chordType

    def spellNoteNames(self):
        self.noteNames = set()
        for string in self.intervalNames:
            name = addIntervalToNoteName(self.rootName, string)
            self.noteNames.add(name)
            if getPitchNumber(name) % 12 == getPitchNumber(self.bassName) % 12:
                self.bassName = name

    def __lt__(self, other):
        return self.complexity < other.complexity


def _test():
    notes = [59, 52, 67, 73]
    c = identifyChord(notes)[0]
    # c.updateName(key='Eb', roman_style=True)
    print(c.name)
    print(c.noteNames)

# if __name__ == '__main__':
# print(addIntervalToNoteName('Bx4', 'P5'))
# _test()
