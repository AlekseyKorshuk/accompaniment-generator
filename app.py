import gradio as gr
import numpy as np
import pretty_midi
from accompaniment_generator.generator.base import Generator


def inference(audio, num_epoch):
    generator = Generator()
    input_midi_data = pretty_midi.PrettyMIDI(audio.name)
    output_midi_data = generator(audio.name, num_epoch=int(num_epoch))
    data = input_midi_data.synthesize()
    input_scaled = np.int16(data / np.max(np.abs(data)) * 32767)
    data = output_midi_data.synthesize()
    output_scaled = np.int16(data / np.max(np.abs(data)) * 32767)
    return [(44100, input_scaled), (44100, output_scaled)]


title = "Accompaniment Generator"
description = "Gradio demo for MIDI-DDSP: Detailed Control of Musical Performance via Hierarchical Modeling. To use it, simply upload your midi file, or click one of the examples to load them. Read more at the links below."

article = "<p style='text-align: center'>" \
          "<a href='https://github.com/AlekseyKorshuk/accompaniment-generator' target='_blank'>Github Repo</a>" \
          "</p>"

examples = [['barbiegirl_mono.mid', 10]]

gr.Interface(
    inference,
    [gr.inputs.File(type="file", label="Input"), gr.inputs.Number(label="Number of epoch", default=10)],
    [gr.outputs.Audio(type="auto", label="Before"), gr.outputs.Audio(type="auto", label="After")],
    title=title,
    description=description,
    article=article,
    examples=examples,
).launch(debug=True)
