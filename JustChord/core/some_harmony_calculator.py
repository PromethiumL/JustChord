from JustChord.core.constants import *
from pprint import pprint


def logger(func):
    def myfunc(*args, **kwargs):
        print(func.__name__, args, kwargs)
        return func(*args, **kwargs)

    return myfunc


def interval_names_to_tone_set(interval_names):
    pitches = list(set([eval(interval) % 12 for interval in interval_names]))
    pitches.sort()
    return pitches


def tone_set_contains(tone_set, subset):
    """
    return whether given pitches or interval exist in some permutations of tone_set
    e.g. {1, 2, 3} contains {0, 1}, also contains{0, 11}

    note that, the tone_set uses absolute pitch, while the subset only gives the pattern. (relative)
    """
    if subset is int:
        subset = (subset,)
    elif subset is not tuple:
        subset = tuple(subset)

    for tp in get_permutations(tone_set):
        s1 = set(subset)
        s2 = set(tp)
        if s1.issubset(s2):
            return True
    return False


def get_all_chords_contain_subset(subset, contain_notes=set()):
    if len(subset) < 2:
        raise Exception('subset {} has too few elements'.format(subset))

    res = []
    for chord_tone_set, chord_type, sonarity in CHORD_DATA:
        # Bypass non-chords
        chord_tone_set = interval_names_to_tone_set(chord_tone_set)
        if len(chord_tone_set) < 3 or 'Scale' in chord_type:
            continue

        for root_pitch in range(12):
            pitches = [(x + root_pitch) % 12 for x in chord_tone_set]
            pitches.sort()
            if tone_set_contains(pitches, subset) and contain_notes.issubset(set(pitches)):
                res.append((DEGREE_NAMES[1][root_pitch], chord_type))
    return res


def get_all_chords_contain_interval(interval: int, contain_notes=set()):
    return get_all_chords_contain_subset((0, interval), contain_notes)


def get_all_chords_contain_notes(note_names):
    if type(note_names) is list:
        pass
    elif type(note_names) is str:
        note_names = [note_names]

    notes = [PITCH_INDEX[name] for name in note_names]
    res = []
    for chord_tone_set, chord_type, sonarity in CHORD_DATA:
        # Skip intervals or scales
        if len(chord_tone_set) < 3 or len(chord_tone_set) > 5:
            continue

        for root_pitch in range(12):
            pitches = [eval(interval) for interval in chord_tone_set]
            pitches = [(p + root_pitch) % 12 for p in pitches]
            pitches.sort()
            if set(notes).issubset(set(pitches)):
                res.append((DEGREE_NAMES[1][root_pitch], chord_type))

    return res


def get_permutations(tone_set):
    result = set()
    for x in tone_set:
        lst = list(tone_set).copy()
        lst = [(p - x) % 12 for p in lst]
        lst.sort()
        result.add(tuple(lst))
    return result


def main1():
    prev_type = ''
    for chord in get_all_chords_contain_notes(['C', 'Bb']):
        if chord[1] != prev_type:
            print()
            prev_type = chord[1]
        print('{} {}'.format(*chord))


if __name__ == '__main__':
    main1()
