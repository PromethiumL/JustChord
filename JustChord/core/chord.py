from JustChord.core.constants import (
    CHORD_DATA,
    DEFAULT_KEY,
    INTERVAL_SIZE,
    PITCH_INDEX,
    USE_ROMAN_STYLE,
)
from JustChord.core.utils import (
    addIntervalToNoteName,
    getInterval,
    getPitchName,
    getPitchNumber,
)


class Chord:
    def __init__(
        self,
        rootName: str,
        intervals: set[int] = None,
        bassName=None,
        chordType=None,
        blankChord=False,
    ):
        if bassName is None:
            bassName = rootName
        self.setRoot(rootName)
        self.setBass(bassName)
        self.name = ""
        self.chordTypes = []
        self.intervals: set[int] = intervals
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

    def buildChord(self) -> None:
        self.chordType = ""
        self.complexity = 0
        self.recognized = False
        s = set()
        for item in CHORD_DATA:
            if self.intervals == set(map(lambda intervalName: (INTERVAL_SIZE[intervalName] % 12), item[0])):
                self.recognized = True
                self.intervalNames = item[0]
                s.add((item[2], item[1]))
                break
        if self.recognized:
            lst = sorted(list(s))
            self.chordType = lst[0][1]
            if self.bassName.upper() != self.rootName.upper():
                self.complexity += 1
                # Inversion increases the complexity.
        else:
            self.chordType = None
            # 'recognized' remains False.

        self.notes = set(map(lambda x: (x + PITCH_INDEX[self.rootName] % 12), list(self.intervals)))

    @staticmethod
    def _romanizeMinorType(typeName):
        """Format chord type for Roman numeral display of a minor chord.

        In Roman notation, lowercase root already implies minor, so:
        - Strip the "m" prefix ("m7" -> "7", "mMaj7" -> "Maj7")
          but not when "m" is part of a word ("minor 3rd" stays)
        - Convert "dim" to "°"
        """
        if typeName == "m" or (
            typeName.startswith("m") and len(typeName) > 1 and not typeName[1].islower()
        ):
            typeName = typeName[1:]
        if typeName.startswith("dim"):
            typeName = "°" + typeName[3:]
        return typeName

    def updateName(self, key=DEFAULT_KEY, roman_style=USE_ROMAN_STYLE):
        if not self.recognized:
            self.buildChord()

        # Spell note names using standard names (Roman numerals can't be used for interval math)
        self.rootName = getPitchName(self.rootPitch, key, roman_style=False)
        self.bassName = getPitchName(self.bassPitch, key, roman_style=False)
        self.typeName = self.chordType
        self.spellNoteNames()

        if self.typeName is None:
            self.typeName = "n.c."
            return self._buildDisplayName()

        # Apply Roman numeral formatting
        if roman_style:
            self.rootName = getPitchName(self.rootPitch, key, roman_style=True)
            self.bassName = getPitchName(self.bassPitch, key, roman_style=True)
            if self.isMinorChord():
                self.rootName = self.rootName.lower()
                self.bassName = self.bassName.lower()
                self.typeName = self._romanizeMinorType(self.typeName)

        return self._buildDisplayName()

    def _buildDisplayName(self):
        inversion = " / " + self.bassName if self.rootName != self.bassName else ""
        self.name = (self.rootName, self.typeName + inversion)

    def parseChordType(self, chordType) -> bool:
        chordType.replace(" ", "")
        for intervals, name, complexity in CHORD_DATA:
            if name == chordType:
                self.complexity = complexity
                self.intervals = intervals
                self.notes = list(map(lambda x: (x + self.rootPitch) % 12, list(intervals)))
                self.chordType = chordType
                return True
        return False

    def isInterval(self):
        return len(self.intervals) == 2 and self.intervals != set([INTERVAL_SIZE["U1"], INTERVAL_SIZE["P5"]])

    def isMinorChord(self):
        return INTERVAL_SIZE["M3"] not in self.intervals and INTERVAL_SIZE["m3"] in self.intervals

    def getBaseName(self, key=DEFAULT_KEY, roman_style=USE_ROMAN_STYLE):
        return getPitchName(self.rootPitch) + " " + self.chordType

    def spellNoteNames(self):
        self.noteNames = set()
        for string in self.intervalNames:
            name = addIntervalToNoteName(self.rootName, string)
            self.noteNames.add(name)
            if getPitchNumber(name) % 12 == getPitchNumber(self.bassName) % 12:
                self.bassName = name

    def __lt__(self, other):
        return self.complexity < other.complexity

    def __repr__(self):
        if not self.recognized:
            return "<unrecognized>"
        else:
            return f"[{self.rootName} {self.typeName}]"


def identifyChord(noteList, key=DEFAULT_KEY, roman_style=USE_ROMAN_STYLE):
    """Make sure that the 'noteList' is non-empty"""
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
            if root == lowestNote:
                chord.complexity -= 3
            results.append(chord)
    results.sort(key=lambda c: c.complexity)
    return results


def identifyChordName(noteArray, key=DEFAULT_KEY, roman_style=USE_ROMAN_STYLE):
    return map(lambda x: x.name, identifyChord(noteArray, key=key, roman_style=roman_style))


def main():
    notes = [59, 52, 67, 73]
    c = identifyChord(notes)[0]
    # c.updateName(key='Eb', roman_style=True)
    print(c.name)
    print(c.noteNames)
    print(c)


if __name__ == "__main__":
    print(addIntervalToNoteName("Bx4", "P5"))
    main()
