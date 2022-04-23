# Global Variables
import math
import random

OPTIONS_M = ((0, -3, 5), (0, -3, 5), (0, -4, 5), (0, -3, 6), (0, -3, 5), (0, -4, 5), (0, -4, 5))
OPTIONS_m = ((0, -4, 5), (0, -4, 5), (0, -3, 5), (0, -3, 5), (0, -4, 5), (0, -3, 6), (0, 5))
MOD_M = ('M', 'm', 'm', 'M', 'M', 'm', 'd')
MOD_m = ('m', 'd', 'M', 'm', 'M', 'M', 'M')


def float_difference(first, second, ndigits=2):
    return round(
        round(first, ndigits) - round(second, ndigits)
        , ndigits
    )


def setTon(line):
    """Return the tonality of the exercise and the bass notes of it"""
    ton = line[:2]
    notes = list(map(int, line[3:].split(' ')))
    if ton[1] == '#':
        ton = (int(ton[0]) * 7) % 12
    else:
        ton = (int(ton[0]) * 5) % 12
    for note in notes:
        if (ton + 6) % 12 == note % 12:
            ton = str((ton - 3) % 12) + 'm'
            break
    else:
        if ton - 3 == notes[-1] % 12:
            ton = str((ton - 3) % 12) + 'm'
        else:
            ton = str(ton) + 'M'
    return ton, notes


def creatChord(nameC, noteF):
    """Create one chord given the name of the chord and the fundamental note"""
    num_funda = int(nameC[:-1])
    if nameC[-1] == 'M':
        val_notes = [num_funda, (num_funda + 4) % 12, (num_funda + 7) % 12]
    elif nameC[-1] == 'm':
        val_notes = [num_funda, (num_funda + 3) % 12, (num_funda + 7) % 12]
    elif nameC[-1] == 'd':
        val_notes = [num_funda, (num_funda + 3) % 12, (num_funda + 6) % 12]

    # Tessitura of each voice
    tenorR = list(range(48, 69))
    contR = list(range(52, 77))
    sopR = list(range(60, 86))

    # Depending in the bass note this are the options for the others voices
    if noteF % 12 == val_notes[0]:
        opc = [[1, 1, 1], [2, 1, 0], [0, 1, 2]]
    elif noteF % 12 == val_notes[1]:
        opc = [[1, 0, 2], [3, 0, 0], [2, 0, 1]]
    elif noteF % 12 == val_notes[2]:
        opc = [[1, 1, 1], [2, 1, 0]]
    else:
        opc = [[1, 1, 1], [2, 1, 0], [0, 1, 2]]

    opc = random.choice(opc)
    chordN = list()
    for num, val in zip(opc, val_notes):
        chordN += [val] * num

    random.shuffle(chordN)

    chord = [noteF, ]
    for nte, voce in zip(chordN, [tenorR, contR, sopR]):
        posible_n = [x for x in voce if x % 12 == nte]
        chord.append(random.choice(posible_n))

    return chord


def selChord(ton, notesBass):
    """Select the chords from all the posibilities"""
    listaOp = OPTIONS_M if ton[-1] == 'M' else OPTIONS_m
    listaMod = MOD_M if ton[-1] == 'M' else MOD_m
    prog = list()

    for note in notesBass:
        name = note % 12
        grad = name - int(ton[:-1])
        grad = math.ceil(((grad + 12) % 12) / 2)
        num = (random.choice(listaOp[grad]) + name + 12) % 12
        grad = num - int(ton[:-1])
        grad = math.ceil(((grad + 12) % 12) / 2)
        name = '{}{}'.format(num, listaMod[grad])
        prog.append([creatChord(name, note), grad])
    return prog


def newChordProg(ton, notes):
    """Create a new individual given the tonality and the base notes"""
    chords = selChord(ton, notes)
    for c in chords:
        yield c


def check_interval(chord):
    """Return the number of mistakes in the distance between the notes."""
    res = 0
    if chord[2] - chord[1] > 12 or chord[2] - chord[1] < 0:
        res += 15
    if chord[3] - chord[2] > 12 or chord[3] - chord[2] < 0:
        res += 15

    if chord[1] == chord[2] or chord[2] == chord[3]:
        res += 1.4
    return res


def check_2_chords(ch1, ch2):
    """Return the number of mistakes in the intervals between 2 chords."""
    res = 0

    # Check for 5° and 8°
    ite1 = map(lambda x, y: y - x, ch1[:-1], ch1[1:])
    ite2 = map(lambda x, y: y - x, ch2[:-1], ch2[1:])
    for inter1, inter2 in zip(ite1, ite2):
        if inter1 == 7 and inter2 == 7:
            res += 15
        elif inter1 == 0 and inter2 == 0:
            res += 15
        elif inter1 == 12 and inter2 == 12:
            res += 15

    # Check for big intervals, just to make it more "human"
    for note1, note2 in zip(ch1[1:], ch2[1:]):
        if abs(note1 - note2) >= 7:  # 7 equals 5° interval
            res += .7

    return res


def neighborhood(iterable):
    """Generator gives the prev actual and next."""
    iterator = iter(iterable)
    prev = None
    item = next(iterator)  # throws StopIteration if empty.
    for nex in iterator:
        yield (prev, item, nex)
        prev = item
        item = nex
    yield (prev, item, None)


def evalNumErr(ton, individual):
    """Evaluation function."""
    res = 0
    for prev, item, nex in neighborhood(individual):
        res += check_interval(item[0])
        if prev == None:
            if item[1] != 0:
                res += 6
            continue
        else:
            if prev[1] in [4, 6] and item[1] in [3, 1]:
                res += 20
            res += check_2_chords(prev[0], item[0])
        if nex == None:
            if item[1] in [1, 2, 3, 4, 5, 6]:
                res += 6
    return (res,)


def mutChangeNotes(ton, individual, indpb, toolbox):
    """Mutant function."""
    new_ind = toolbox.clone(individual)
    for x in range(len(individual[0])):
        if random.random() < indpb:
            listaOp = OPTIONS_M if ton[-1] == 'M' else OPTIONS_m
            listaMod = MOD_M if ton[-1] == 'M' else MOD_m

            note = individual[x][0][0]

            name = note % 12
            grad = name - int(ton[:-1])
            grad = math.ceil(((grad + 12) % 12) / 2)
            num = (random.choice(listaOp[grad]) + name + 12) % 12
            grad = num - int(ton[:-1])
            grad = math.ceil(((grad + 12) % 12) / 2)
            name = '{}{}'.format(num, listaMod[grad])

            new_ind[x] = [creatChord(name, note), grad]

    del new_ind.fitness.values
    return new_ind,
