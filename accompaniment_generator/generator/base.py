from typing import List
import music21.stream
import numpy
import pretty_midi
from accompaniment_generator.utils.base import initial_chords, evaluate, individual_mutation, Chord
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import tqdm
from pretty_midi.pretty_midi import Note
import copy
from music21 import converter


class Generator:
    """
    Generator class to create accompaniments with Evolutionary algorithm
    """

    def __init__(self):
        """
        Generator constructor
        """
        self.chord_duration = None

    def preprocess(self,
                   music21_score: music21.stream.Stream,
                   input_midi_data: pretty_midi.PrettyMIDI,
                   chord_duration: float = None
                   ):
        """
        Preprocessing data to forward
        :param music21_score: Score by Music21
        :param input_midi_data: Input MIDI data as PrettyMIDI
        :param chord_duration: Custom chord duration
        :return: List of Notes, Tonic and Tonic name
        """
        self.chord_duration = chord_duration
        if chord_duration is None:
            self.chord_duration = input_midi_data.resolution * \
                                  input_midi_data.get_tempo_changes()[1][0] / 100000 * 2

        key = music21_score.analyze('key')
        return input_midi_data.instruments[0].notes, key.tonic.name, key.mode

    def forward(self,
                tonic: str,
                notes: List[Note],
                verbose: bool,
                num_epoch: int,
                mutpb: float,
                cxpb: float,
                ngen: float,
                population_size: int,
                best_number: int,
                tonic_value: str
                ) -> tools.HallOfFame:
        """
        Generates accompaniment based on input data
        :param tonic: Tonic of the music
        :param notes: List of Notes
        :param verbose: Whenever to log the process
        :param num_epoch: Number of epoch to train
        :param mutpb: The probability of mutating an individual.
        :param cxpb: The probability of mating two individuals.
        :param ngen: The number of generation.
        :param population_size: Size of the population
        :param best_number: Number of the best accompaniments to store
        :param tonic_value: Tonic key value
        :return: Hall of fame with the best individuals
        """
        # ========================= GA setup =========================
        creator.create('FitnessMin', base.Fitness, weights=(1.0,))
        creator.create('Individual', list, fitness=creator.FitnessMin)

        toolbox = base.Toolbox()
        toolbox.register('creat_notes', initial_chords, notes, self.chord_duration)
        toolbox.register('individual', tools.initIterate, creator.Individual,
                         toolbox.creat_notes)
        toolbox.register('population', tools.initRepeat, list, toolbox.individual)

        toolbox.register('evaluate', evaluate, tonic, notes, tonic_value)
        toolbox.register('mate', tools.cxOnePoint)
        toolbox.register('mutate', individual_mutation, toolbox=toolbox)
        toolbox.register('select', tools.selTournament, tournsize=3)
        # =============================================================

        pop = toolbox.population(n=population_size)
        hof = tools.HallOfFame(best_number)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register('avg', numpy.mean)
        stats.register('std', numpy.std)
        stats.register('min', numpy.min)
        stats.register('max', numpy.max)

        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb, ngen=ngen, stats=stats, halloffame=hof,
                                       verbose=verbose)
        for _ in tqdm.tqdm(range(num_epoch)):
            pop, log = algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb, ngen=ngen, stats=stats, halloffame=hof,
                                           verbose=verbose)
        return hof

    def postprocess(self,
                    input_midi_data: pretty_midi.PrettyMIDI,
                    outputs: tools.HallOfFame
                    ) -> List[pretty_midi.PrettyMIDI]:
        """
        Postprocessing of the resulting accompaniment
        :param input_midi_data: Input MIDI data as PrettyMIDI
        :param outputs: Hall of fame with the best individuals
        :return: List of resulting MIDI data
        """
        output_midi_data = []
        octaves_unique = []
        for output in outputs:
            input_midi_data_temp = copy.deepcopy(input_midi_data)
            instrument_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
            instrument = pretty_midi.Instrument(program=instrument_program, name="Accompaniment")
            octaves = [pretty_midi.note_number_to_name(chord.notes[0].pitch) for chord in output]
            if octaves in octaves_unique:
                continue
            for i, chord in enumerate(output):
                for note in chord.notes:
                    if i == len(output) - 1:
                        note.end = input_midi_data.get_end_time()
                    instrument.notes.append(note)
            input_midi_data_temp.instruments.append(instrument)
            # input_midi_data_temp.instruments[0].notes += instrument.notes
            output_midi_data.append(input_midi_data_temp)
            octaves_unique.append(octaves)
        return output_midi_data

    def __call__(self,
                 midi_file_path: str,
                 verbose: bool = False,
                 num_epoch: int = 10,
                 chord_duration: float = None,
                 mutpb: float = 0.3,
                 cxpb: float = 0.5,
                 ngen: float = 40,
                 population_size: int = 400,
                 best_number: int = 3
                 ) -> List[pretty_midi.PrettyMIDI]:
        """
        Call to generate accompaniment
        :param midi_file_path: File name or path to MIDI file
        :param notes: List of Notes
        :param verbose: Whenever to log the process
        :param num_epoch: Number of epoch to train
        :param mutpb: The probability of mutating an individual.
        :param cxpb: The probability of mating two individuals.
        :param ngen: The number of generation.
        :param population_size: Size of the population
        :param best_number: Number of the best accompaniments to store
        :return: List of resulting MIDI data
        """
        input_midi_data = pretty_midi.PrettyMIDI(midi_file_path)
        music21_score = converter.parse(midi_file_path)
        notes, tonic_value, tonic = self.preprocess(music21_score, input_midi_data, chord_duration)
        outputs = self.forward(tonic, notes, verbose, num_epoch, mutpb, cxpb, ngen, population_size, best_number,
                               tonic_value)
        output_midi_data = self.postprocess(input_midi_data, outputs)
        return output_midi_data
