import streamlit as st
from pathlib import Path
from PIL import Image

st.header("Financial Research")

st.write("We're working on it.")

construction_gif_path = Path("/users/cg/Documents/Personal/Projects/Capstone_Project/Supplemental/Sitting_on_beam.jpeg")

construction = Image.open(construction_gif_path)

st.image(construction)