import json
from pathlib import Path

marks = ["b♮#"]

DEGREE_NAMES = [[], [], [], []]
DEGREE_NAMES[0] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"] * 2
DEGREE_NAMES[1] = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"] * 2
DEGREE_NAMES[2] = [
    "I",
    "#II",
    "II",
    "#II",
    "III",
    "IV",
    "#IV",
    "V",
    "#V",
    "VI",
    "#VI",
    "VII",
] * 2
DEGREE_NAMES[3] = [
    "I",
    "bII",
    "II",
    "bIII",
    "III",
    "IV",
    "bV",
    "V",
    "bVI",
    "VI",
    "bVII",
    "VII",
] * 2

KEY_LIST = [[], []]
KEY_LIST[0] = ["G", "D", "A", "E", "B", "F#", "C#"]
KEY_LIST[1] = ["F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb"]

NATURAL_SCALES = {
    "Gb": ["Cb", "Db", "Eb", "F", "Gb", "Ab", "Bb"],
    "Db": ["C", "Db", "Eb", "F", "Gb", "Ab", "Bb"],
    "Ab": ["C", "Db", "Eb", "F", "G", "Ab", "Bb"],
    "Eb": ["C", "D", "Eb", "F", "G", "Ab", "Bb"],
    "Bb": ["C", "D", "Eb", "F", "G", "A", "Bb"],
    "F": ["C", "D", "E", "F", "G", "A", "Bb"],
    "C": ["C", "D", "E", "F", "G", "A", "B"],
    "G": ["C", "D", "E", "F#", "G", "A", "B"],
    "D": ["C#", "D", "E", "F#", "G", "A", "B"],
    "A": ["C#", "D", "E", "F#", "G#", "A", "B"],
    "E": ["C#", "D#", "E", "F#", "G#", "A", "B"],
    "B": ["C#", "D#", "E", "F#", "G#", "A#", "B"],
    "F#": ["C#", "D#", "E#", "F#", "G#", "A#", "B"],
}

DEFAULT_KEY = "C"
USE_ROMAN_STYLE = False

PITCH_INDEX = {
    "Cbb": -2,
    "Cb": -1,
    "C": 0,
    "C#": 1,
    "Cx": 2,
    "Db": 1,
    "Dbb": 0,
    "D": 2,
    "D#": 3,
    "Dx": 4,
    "Ebb": 2,
    "Eb": 3,
    "E": 4,
    "E#": 5,
    "Fb": 4,
    "F": 5,
    "F#": 6,
    "Fx": 7,
    "Gbb": 5,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Gx": 9,
    "Abb": 7,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Ax": 11,
    "Bbb": 9,
    "Bb": 10,
    "B": 11,
    "B#": 12,
    "Bx": 13,
}

INTERVALS = [
    "unison",
    "m2",
    "M2",
    "m3",
    "M3",
    "Perfect M3th",
    "Tritone",
    "Perfect 5th",
    "m6",
    "M6",
    "m7",
    "M7",
]

INTERVAL_SIZE = {
    "U1": 0,
    "m2": 1,
    "m9": 1,
    "d9": 1,
    "M2": 2,
    "M9": 2,
    "A9": 3,
    "A2": 3,
    "m3": 3,
    "M3": 4,
    "d4": 4,
    "P4": 5,
    "P11": 5,
    "A4": 6,
    "A11": 6,
    "TT": 6,
    "d5": 6,
    "P5": 7,
    "A5": 8,
    "m6": 8,
    "m13": 8,
    "M13": 9,
    "M6": 9,
    "A6": 10,
    "d7": 9,
    "m7": 10,
    "M7": 11,
}


def _load_chord_data():
    data_path = Path(__file__).resolve().parent.parent.parent / "data" / "chords.jsonc"
    with open(data_path) as f:
        # Strip // comments for JSONC support
        stripped = "\n".join(line.split("//")[0] for line in f)
    raw = json.loads(stripped)
    return [(set(entry["intervals"]), entry["name"], entry["complexity"]) for entry in raw]


CHORD_DATA = _load_chord_data()
