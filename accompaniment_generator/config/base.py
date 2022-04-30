major_keys = {
    'C': ['C', 'Dm', 'Em', 'F', 'G', 'Am', 'Bo'],
    'C#': ['C#', 'D#m', 'E#m', 'F#', 'G#', 'A#m', 'B#o'],
    'Db': ['Db', 'Ebm', 'Fm', 'Gb', 'Ab', 'Bbm', 'Co'],
    'D': ['D', 'Em', 'F#m', 'G', 'A', 'Bm', 'C#o'],
    'Eb': ['Eb', 'Fm', 'Gm', 'Ab', 'Bb', 'Cm', 'Do'],
    'E': ['E', 'F#m', 'G#m', 'A', 'B', 'C#m', 'D#o'],
    'F': ['F', 'Gm', 'Am', 'Bb', 'C', 'Dm', 'Eo'],
    'F#': ['F#', 'G#m', 'A#m', 'B', 'C#', 'D#m', 'E#o'],
    'Gb': ['Gb', 'Abm', 'Bbm', 'Cb', 'Db', 'Ebm', 'Fo'],
    'G': ['G', 'Am', 'Bm', 'C', 'D', 'Em', 'F#o'],
    'Ab': ['Ab', 'Bbm', 'Cm', 'Db', 'Eb', 'Fm', 'Go'],
    'A': ['A', 'Bm', 'C#m', 'D', 'E', 'F#m', 'G#o'],
    'Bb': ['Bb', 'Cm', 'Dm', 'Eb', 'F', 'Gm', 'Ao'],
    'B': ['B', 'C#m', 'D#m', 'E', 'F#', 'G#m', 'A#o']
}

minor_keys = {
    "Cm": ["Cm", "Do", "Eb", "Fm", "Gm", "Ab", "Bb"],
    "C#m": ["C#m", "D#o", "E", "F#m", "G#m", "A", "B"],
    "Dm": ["Dm", "Eo", "F", "Gm", "Am", "Bb", "C"],
    "D#m": ["D#m", "E#o", "F#", "G#m", "A#m", "B", "C#"],
    "Ebm": ["Ebm", "Fo", "Gb", "Abm", "Bbm", "Cb", "Db"],
    "Em": ["Em", "F#o", "G", "Am", "Bm", "C", "D"],
    "Fm": ["Fm", "Go", "Ab", "Bbm", "Cm", "Db", "Eb"],
    "F#m": ["F#m", "G#o", "A", "Bm", "C#m", "D", "E"],
    "Gm": ["Gm", "Ao", "Bb", "Cm", "Dm", "Eb", "F"],
    "G#m": ["G#m", "A#o", "B", "C#m", "D#m", "E", "F#"],
    "Abm": ["Abm", "Bbo", "Cb", "Dbm", "Ebm", "Fb", "Gb"],
    "Am": ["Am", "Bo", "C", "Dm", "Em", "F", "G"],
    "A#m": ["A#m", "B#o", "C#", "D#m", "E#m", "F#", "G#"],
    "Bbm": ["Bbm", "Co", "Db", "Ebm", "Fm", "Gb", "Ab"],
    "Bm": ["Bm", "C#o", "D", "Em", "F#m", "G", "A"]
}

matcher = {
    "C#": "Db",
    "D#": "Eb",
    "F#": "Gb",
    "G#": "Ab",
    "A#": "Bb",
}

chord_types = {
    "major": {
        "base_note": {
            "start": 36,
            "end": 47,
        },
        "shifts": [0, 4, 7],
    },
    "minor": {
        "base_note": {
            "start": 36,
            "end": 47,
        },
        "shifts": [0, 3, 7],
    },
    "diminished": {
        "base_note": {
            "start": 36,
            "end": 47,
        },
        "shifts": [0, 3, 6],
    },
    "suspended_second": {
        "base_note": {
            "start": 36,
            "end": 47,
        },
        "shifts": [0, 2, 7],
    },
    "suspended_fourth": {
        "base_note": {
            "start": 36,
            "end": 47,
        },
        "shifts": [0, 5, 7],
    },
    "major_first_inversion": {
        "base_note": {
            "start": 36,
            "end": 47,
        },
        "shifts": [0, 3, 9],
    },
    "minor_first_inversion": {
        "base_note": {
            "start": 36,
            "end": 47,
        },
        "shifts": [0, 4, 9],
    },
    "major_second_inversion": {
        "base_note": {
            "start": 36,
            "end": 47,
        },
        "shifts": [0, 3, 9],
    },
    "minor_second_inversion": {
        "base_note": {
            "start": 36,
            "end": 47,
        },
        "shifts": [0, 5, 8],
    },
}
