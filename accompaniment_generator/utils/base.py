import random
from typing import List, Any
import numpy as np
from deap import base
from pretty_midi import Note
from pychord import find_chords_from_notes
import pretty_midi
from accompaniment_generator.config.base import major_keys, minor_keys, matcher, chord_types


def get_allowed_chords(tonic: str, key: str) -> List[str]:
    """
    Return allowed chords
    :param tonic: Tonic of the music
    :param key: Key chord
    :return: List of allowed chords
    """
    if tonic == "major":
        dict_to_search = major_keys
    else:
        dict_to_search = minor_keys
        key += "m"
    if key not in dict_to_search:
        return dict_to_search[matcher[key]]
    return dict_to_search[key]


def get_chord_from_pitches(pitches: List[int]) -> str:
    """
    Returns chord from list of pitches
    :param pitches: List of pitches
    :return: Chord name
    """
    notes = [pretty_midi.note_number_to_name(pitch) for pitch in pitches]
    for i, note in enumerate(notes):
        note_name = ''.join(i for i in note if not i.isdigit())
        notes[i] = note_name.replace("-", "")
    result = find_chords_from_notes(notes)
    return result[0].chord.replace("dim", "o")


class Chord:

    def __init__(self, pitches: List[int], start: float, end: float, velocity: int = 50):
        """
        Chord constructor
        :param pitches: List of pitches
        :param start: Starting time
        :param end: Ending time
        :param velocity: Velocity of the chord
        """
        self.velocity = velocity
        self.type = None
        pitches = sorted(pitches)
        self.notes = [
            Note(
                pitch=pitch, start=start, end=end, velocity=self.velocity
            ) for pitch in pitches
        ]

    def get_base_note(self):
        """
        Returns base note of the chord
        :return: Base note
        """
        return self.notes[0].pitch % 12

    def is_note_exist(self, note: Note) -> bool:
        """
        Returns whenever note is in the chord
        :param note: Note
        :return: True if exists, otherwise False
        """
        for _note in self.notes:
            if _note.pitch == note:
                return True
        return False

    def get_pitches(self) -> List[int]:
        """
        Returns list of chord pitches
        :return: List of chord pitches
        """
        return [note.pitch for note in self.notes]


def float_difference(first, second, ndigits=2) -> float:
    """
    Returns difference of two float values
    :param first: First float valur
    :param second: Second float value
    :param ndigits: Number of digits to round
    :return: Float difference
    """
    return round(
        round(first, ndigits) - round(second, ndigits)
        , ndigits
    )


def chord_from_params(params: dict) -> Chord:
    """
    Returns Chord based on parameters
    :param params: Parameters as dict
    :return: Chord
    """
    base_note = np.random.randint(
        params["base_note"]["start"],
        params["base_note"]["end"],
    )
    pitches = [base_note + shift for shift in params["shifts"]]
    return Chord(pitches, 0, 0, 50)


def get_random_chord() -> Chord:
    """
    Returns random Chord
    :return: Chord
    """
    chord_type, params = random.choice(list(chord_types.items()))
    chord = chord_from_params(params)
    chord.type = chord_type
    return chord


def initial_chords(notes: List[Note], duration: float = 0.96):
    """
    Create a new individual given its notes and duration
    :param notes: Notes
    :param duration: Chord duration
    :return: Yield chord
    """
    num_chords = int(notes[-1].end // duration)
    for i in range(num_chords):
        chord = get_random_chord()
        for note in chord.notes:
            note.start = i * duration
            note.end = (i + 1) * duration
        yield chord


def get_note_at_time(t: float, notes: List[Note]) -> int:
    """
    Returns note pitch that plays at input time
    :param t: Time
    :param notes: List of notes
    :return: Note pitch if such note exists, else -1
    """
    for note in notes[::-1]:
        if round(note.start, 2) <= t:
            return note.pitch
    for note in notes:
        if round(note.start, 2) <= t < round(note.end, 2):
            return note.pitch
    return -1


def check_interval(chord: Chord) -> float:
    """
    Return the number of mistakes in the distance between the notes
    :param chord: Input Chord
    :return: Resulting score
    """
    res = 0
    if chord.notes[2].pitch - chord.notes[1].pitch > 12 or \
            chord.notes[2].pitch - chord.notes[1].pitch < 0:
        res += 15
    if chord.notes[1].pitch == chord.notes[2].pitch:
        res += 1.4
    return res


def neighborhood(iterable: Any):
    """
    Generator gives the prev actual and next
    :param iterable: Iterable list of chords
    :return: Yield tuple of previous, current and next chords
    """
    iterator = iter(iterable)
    prev = None
    item = next(iterator)
    for nex in iterator:
        yield (prev, item, nex)
        prev = item
        item = nex
    yield (prev, item, None)


def evaluate(tonic: str, notes: List[Note], tonic_value: str, individual: List[Chord]) -> List[float]:
    """
    Evaluation function
    :param tonic: Tonic of the music
    :param notes: List of notes
    :param tonic_value: Tonic key value
    :param individual: List of chords
    :return: Score
    """
    score = 0.0
    allowed = get_allowed_chords(tonic, tonic_value)

    for i, (previous_chord, current_chord, next_chord) in enumerate(neighborhood(individual)):
        score -= check_interval(current_chord)
        t = current_chord.notes[0].start  # calculating the current time of the midi
        if abs(current_chord.notes[0].pitch - get_note_at_time(t, notes)) % 12 == 0 and abs(
                current_chord.notes[0].pitch - get_note_at_time(t, notes)) / 12 == 2:
            score += 1000

        if current_chord.notes[0].pitch - 12 == get_note_at_time(t, notes):
            score += 25
        else:
            score -= 10

        if get_chord_from_pitches(current_chord.get_pitches()) in allowed:
            score += 30
        else:
            score -= 30
    octaves = [pretty_midi.note_number_to_name(chord.notes[0].pitch)[-1] for chord in individual]
    score -= len(set(octaves)) * 100

    if individual[0].get_pitches() == individual[-1].get_pitches():
        score += 100

    return score,


def mutate_chord(chord) -> Chord:
    """
    Returns new mutated chord based on the given
    :param chord: Chord to mutate
    :return: Resulting chord
    """
    new_chord = get_random_chord()
    for note in new_chord.notes:
        note.start = chord.notes[0].start
        note.end = chord.notes[0].end
    return new_chord


def individual_mutation(individual: List[Chord], toolbox: base.Toolbox) -> List[Any]:
    """
    Mutant function
    :param individual: List of chords
    :param toolbox: Toolbox for evolution
    :return: New individual
    """
    new_ind = toolbox.clone(individual)
    index = random.randint(0, len(new_ind) - 1)
    new_ind[index] = mutate_chord(new_ind[index])
    del new_ind.fitness.values
    return new_ind,
