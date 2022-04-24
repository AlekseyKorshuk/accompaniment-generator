import streamlit as st
from accompaniment_generator.generator.base import Generator
import uuid
from midi2audio import FluidSynth

ABOUT_TEXT = "🤗 Accompaniment Generator - generate accompaniment part with chords using Evolutionary algorithm."
CONTACT_TEXT = """
_Built by Aleksey Korshuk with love_ ❤️ 
[![Follow](https://img.shields.io/github/followers/AlekseyKorshuk?style=social)](https://github.com/AlekseyKorshuk)

[![Follow](https://img.shields.io/twitter/follow/alekseykorshuk?style=social)](https://twitter.com/intent/follow?screen_name=alekseykorshuk)

Star project repository:
[![GitHub stars](https://img.shields.io/github/stars/AlekseyKorshuk/accompaniment-generator?style=social)](https://github.com/AlekseyKorshuk/accompaniment-generator)
"""
st.sidebar.markdown(
    """
<style>
.aligncenter {
    text-align: center;
}
</style>
<p class="aligncenter">
    <img src="https://seeklogo.com/images/A/apple-music-logo-4FBA5FADCC-seeklogo.com.png" width="220" />
</p>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown(ABOUT_TEXT)
st.sidebar.markdown(CONTACT_TEXT)


def inference(audio, num_epoch):
    generator = Generator()
    output_midi_data = generator(audio, num_epoch=int(num_epoch))
    name = uuid.uuid4()
    output_midi_data.write(f'{name}.mid')
    fs = FluidSynth("font.sf2")
    fs.midi_to_audio(f'{name}.mid', f'{name}.wav')
    fs.midi_to_audio(audio, f'{name}-init.wav')
    # time.sleep(2)
    print([f'{name}-init.wav', f'{name}.wav'])
    return f'{name}-init.wav', f'{name}.wav'


st.title("Accompaniment Generator")

st.markdown(
    "App to generate accompaniment for MIDI music file with Evolutionary algorithm. Check out [project repository](https://github.com/AlekseyKorshuk/accompaniment-generator).")

article = "<p style='text-align: center'>" \
          "<a href='https://github.com/AlekseyKorshuk/accompaniment-generator' target='_blank'>Github Repo</a>" \
          "</p>"

from os import listdir
from os.path import isfile, join

onlyfiles = [f for f in listdir("./examples") if isfile(join("./examples", f))]

model_name = st.selectbox(
    'Select example MIDI file (will be used only for empty file field):',
    onlyfiles
)

uploaded_file = st.file_uploader(
    'Upload MIDI file:'
)

num_epoch = st.number_input("Number of epochs:",
                            min_value=1,
                            max_value=1000,
                            step=1,
                            value=10,
                            )

generate_image_button = st.button("Generate")

if generate_image_button:
    input_file = f"./examples/{model_name}"
    if uploaded_file is not None:
        input_file = uploaded_file.name
    with st.spinner(text=f"Generating, this may take some time..."):
        before, after = inference(input_file, num_epoch)
    st.markdown("Before:")
    st.audio(before)
    st.markdown("After:")
    st.audio(after)
