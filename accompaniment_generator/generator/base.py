from typing import Tuple, List

import numpy
import pretty_midi

from accompaniment_generator.utils.base import float_difference, setTon, newChordProg, evalNumErr, mutChangeNotes

from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import tqdm

class Generator:

    def preprocess(self,
                   input_midi_data: pretty_midi.PrettyMIDI,
                   ton: str = "2b"
                   ) -> Tuple[str, List[int]]:
        notes = []
        for note in input_midi_data.instruments[0].notes:
            for i in range(int((note.end - note.start) // 0.24)):
                notes.append(str(note.pitch))
        return setTon(f"{ton} {' '.join(notes)}")

    def forward(self, ton: str, notes: list, verbose: bool, num_epoch: int) -> list:
        # ========================= GA setup =========================
        creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
        creator.create('Individual', list, fitness=creator.FitnessMin)

        toolbox = base.Toolbox()
        toolbox.register('creat_notes', newChordProg, ton, notes)
        toolbox.register('individual', tools.initIterate, creator.Individual,
                         toolbox.creat_notes)
        toolbox.register('population', tools.initRepeat, list, toolbox.individual)

        toolbox.register('evaluate', evalNumErr, ton)
        toolbox.register('mate', tools.cxOnePoint)
        toolbox.register('mutate', mutChangeNotes, ton, indpb=0.4, toolbox=toolbox)
        toolbox.register('select', tools.selTournament, tournsize=3)
        # =============================================================

        pop = toolbox.population(n=400)
        hof = tools.HallOfFame(3)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register('avg', numpy.mean)
        stats.register('std', numpy.std)
        stats.register('min', numpy.min)
        stats.register('max', numpy.max)

        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.3, ngen=70, stats=stats, halloffame=hof,
                                       verbose=verbose)
        for _ in tqdm.tqdm(range(num_epoch)):
            # pop = toolbox.population(n=400)
            pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.3, ngen=70, stats=stats, halloffame=hof,
                                           verbose=verbose)

        result = [x[0] for x in hof[0]]
        # for best in hof:
        #     print([x[0] for x in best], end='\n============\n')
        return result

    def postprocess(self,
                    input_midi_data: pretty_midi.PrettyMIDI,
                    outputs: list
                    ) -> pretty_midi.PrettyMIDI:
        notes = input_midi_data.instruments[0].notes
        ids = []
        for i, note in enumerate(notes):
            if i - 1 >= 0 and \
                    float_difference(notes[i - 1].end, notes[i - 1].start) < 0.48 and \
                    i - 1 in ids and \
                    float_difference(notes[i].end, notes[i].start) < 0.48:
                continue
            ids.append(i)

        instrument_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
        instrument = pretty_midi.Instrument(program=instrument_program, name="Accompaniment")
        for id in ids:
            if len(outputs) <= id:
                break
            note = input_midi_data.instruments[0].notes[id]
            for chord_note in outputs[id]:
                new_note = pretty_midi.Note(velocity=50, pitch=chord_note, start=note.start, end=note.start + 0.48)
                instrument.notes.append(new_note)
        input_midi_data.instruments.append(instrument)
        return input_midi_data

    def __call__(self, midi_file_path: str, ton: str = "2b", verbose: bool = False, num_epoch: int = 10):
        input_midi_data = pretty_midi.PrettyMIDI(midi_file_path)
        ton, notes = self.preprocess(input_midi_data, ton)
        outputs = self.forward(ton, notes, verbose, num_epoch)
        output_midi_data = self.postprocess(input_midi_data, outputs)
        return output_midi_data
