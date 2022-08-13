import streamlit as st
from pathlib import Path
from PIL import Image
import urllib.request

st.header("Financial Research")

st.write("We're working on it.")

urllib.request.urlretrieve("https://github.com/CamGould/Financial_Compass/blob/main/supplemental/Sitting_on_beam.jpeg?raw=true", "working.png")

construction = Image.open("working.png")

st.image(construction)