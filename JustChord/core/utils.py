import re
from JustChord.core.constants import *


def getPitchNumber(name):
    """returns the midi pitch number of the given noteName"""
    result = re.match(r'[A-G](b{1,2}|x|#|\*|n)?', name)
    if not result:
        raise Exception('Invalid note name: {}'.format(name))
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
    if interval not in INTERVAL_SIZE:
        raise Exception("Incorrect interval: {}".format(interval))

    pitch = getPitchNumber(name)
    letter = name[0]
    octave = ''.join(list(filter(lambda x: ord('0') <= ord(x) <= ord('9'), list(name))))
    # print("name: {}".format(octave))
    newPitch = pitch + INTERVAL_SIZE[interval]
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
