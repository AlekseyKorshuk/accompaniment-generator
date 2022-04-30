import random
import numpy as np
from pretty_midi import Note
from pychord import find_chords_from_notes
import pretty_midi

from accompaniment_generator.config.base import major_keys, minor_keys, matcher, chord_types


def get_allowed_chords(tonic: str, key: str):
    if tonic == "major":
        dict_to_search = major_keys
    else:
        dict_to_search = minor_keys
        key += "m"
    if key not in dict_to_search:
        return dict_to_search[matcher[key]]
    return dict_to_search[key]


def get_chord_from_pitches(pitches: list):
    notes = [pretty_midi.note_number_to_name(pitch) for pitch in pitches]
    for i, note in enumerate(notes):
        note_name = ''.join(i for i in note if not i.isdigit())
        notes[i] = note_name.replace("-", "")
    result = find_chords_from_notes(notes)
    return result[0].chord.replace("dim", "o")


class Chord:

    def __init__(self, pitches: list, start: float, end: float, velocity: int = 50):
        self.velocity = velocity
        self.type = None
        pitches = sorted(pitches)
        self.notes = [
            Note(
                pitch=pitch, start=start, end=end, velocity=self.velocity
            ) for pitch in pitches
        ]

    def get_base_note(self):
        return self.notes[0].pitch % 12

    def is_note_exist(self, note):
        for _note in self.notes:
            if _note.pitch == note:
                return True
        return False

    def get_pitches(self):
        return [note.pitch for note in self.notes]


def float_difference(first, second, ndigits=2):
    return round(
        round(first, ndigits) - round(second, ndigits)
        , ndigits
    )


def chord_from_params(params):
    base_note = np.random.randint(
        params["base_note"]["start"],
        params["base_note"]["end"],
    )
    pitches = [base_note + shift for shift in params["shifts"]]
    return Chord(pitches, 0, 0, 50)


def get_random_chord() -> Chord:
    chord_type, params = random.choice(list(chord_types.items()))
    chord = chord_from_params(params)
    chord.type = chord_type
    return chord


def initial_chords(notes, duration=0.96):
    """Create a new individual given the tonality and the base notes"""
    num_chords = int(notes[-1].end // duration)
    for i in range(num_chords):
        chord = get_random_chord()
        for note in chord.notes:
            note.start = i * duration
            note.end = (i + 1) * duration
        yield chord


def get_note_at_time(t, notes):
    for note in notes[::-1]:
        if round(note.start, 2) <= t:
            return note.pitch
    for note in notes:
        if round(note.start, 2) <= t < round(note.end, 2):
            return note.pitch
    return -1


def check_interval(chord: Chord):
    """Return the number of mistakes in the distance between the notes."""
    res = 0
    if chord.notes[2].pitch - chord.notes[1].pitch > 12 or \
            chord.notes[2].pitch - chord.notes[1].pitch < 0:
        res += 15
    if chord.notes[1].pitch == chord.notes[2].pitch:
        res += 1.4
    return res


def neighborhood(iterable):
    """Generator gives the prev actual and next."""
    iterator = iter(iterable)
    prev = None
    item = next(iterator)
    for nex in iterator:
        yield (prev, item, nex)
        prev = item
        item = nex
    yield (prev, item, None)


def mean_score(individual):
    pitch_sum = 0
    for i in individual:
        pitch_sum += i.notes[0].pitch
    mean_note = pitch_sum / len(individual)
    mean_deviation = 0
    for i in individual:
        mean_deviation += (i.notes[0].pitch - mean_note) ** 2
    return (mean_deviation ** 0.5) / 2


def evalNumErr(ton, notes, individual):
    """Evaluation function."""
    score = 0
    for i, (previous_chord, current_chord, next_chord) in enumerate(neighborhood(individual)):
        score -= check_interval(current_chord)
        t = current_chord.notes[0].start  # calculating the current time of the midi
        if abs(current_chord.notes[0].pitch - get_note_at_time(t, notes)) % 12 == 0:
            score += 1000
        # if (current_chord.get_base_note() == get_note_at_time(t, notes) % 12) and (
        #         current_chord.notes[0].pitch <= get_note_at_time(t, notes)):
        #     score += 50

        if current_chord.is_note_exist(get_note_at_time(t, notes)):
            score += 5

        if current_chord.notes[0].pitch - 12 == get_note_at_time(t, notes):
            score += 25
        else:
            score -= 10

        # if previous_chord is not None:
        # if "suspended" in previous_chord.type and "suspended" in current_chord.type:
        #     score -= 5

        # if previous_chord.get_pitches() == current_chord.get_pitches():
        #     score -= 10

        note_name = pretty_midi.note_number_to_name(individual[0].notes[0].pitch)
        note_name = ''.join(i for i in note_name if not i.isdigit())
        note_name = note_name.replace("-", "")
        allowed = get_allowed_chords(ton, note_name)
        if get_chord_from_pitches(current_chord.get_pitches()) in allowed:
            score += 30
        else:
            score -= 30
    octaves = [pretty_midi.note_number_to_name(chord.notes[0].pitch)[-1] for chord in individual]
    score -= len(set(octaves)) * 10

    # types = [chord.type for chord in individual]
    # score += types.count(ton) * 125
    # score += (len(individual) - len(set(types))) * 100
    return score,


def mutate_chord(chord):
    new_chord = get_random_chord()
    for note in new_chord.notes:
        note.start = chord.notes[0].start
        note.end = chord.notes[0].end
    return new_chord


def mutChangeNotes(ton, individual, indpb, toolbox):
    """Mutant function."""
    new_ind = toolbox.clone(individual)

    # index = random.randint(0, len(individual)-1)
    # new_ind[index] = mutate_chord(individual[index])
    for i, chord in enumerate(new_ind):
        new_ind[i] = mutate_chord(chord)

    del new_ind.fitness.values
    return new_ind,
