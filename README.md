# Accompaniment generator

Generate accompaniment part with chords using Evolutionary algorithm.

[![Demo](https://i.postimg.cc/Xq7QKDTp/Before-2.png)](https://postimg.cc/34VXY9rT)

# Use with Spaces

Live web app for easiest inference available
here: [link](https://huggingface.co/spaces/AlekseyKorshuk/accompaniment-generator)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://huggingface.co/spaces/AlekseyKorshuk/accompaniment-generator)

# Installation

Directly with pip:

```bash
pip install git+https://github.com/AlekseyKorshuk/accompaniment-generator
```

Or by cloning this repository:

```bash
git clone https://github.com/AlekseyKorshuk/accompaniment-generator
%cd accompaniment-generator
pip install .
```

# How to use

```python
from accompaniment_generator.generator.base import Generator

generator = Generator()
output_midi_data = generator("input.mid", num_epoch=10)
output_midi_data[0].write("output.mid")
```

# Limitations

There are some basic limitations:

- My knowledge of Music Theory
    - It is really hard to understand it in such short period of time from very zero, therefore some results are not archivable by human reasons.
- Computationally-intensive
    - Because of the many possible options of chord for each place.
- Near-optimal solution
    - Due to algorithm definition a near-optimal solution can be found with it.
- Mutation
    - Sometimes it is not possible to get the best result because of random mutation.
- Evaluation
    - Evaluation function require an excellent  knowledge of the task that this algorithm is going to solve, therefore some results are not archivable by human reasons.
