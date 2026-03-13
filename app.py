import argparse
import streamlit as st
from pathlib import Path
from src.image_search import ImageSearchApp
from src.navigation import load_navigation_css
from pages.home import load_home
from pages.login import load_login

parser = argparse.ArgumentParser(description="Vector Search CLIP Application")
parser.add_argument("--port", type=int, default=8501, help="Port number for Streamlit app (default: 8501)")
parser.add_argument("--embedded_data", type=str, default="embedded_data", help="Directory containing the index (default: embedded_data)")
parser.add_argument("--model", type=str, default="openai/clip-vit-base-patch32", help="CLIP model to use (default: openai/clip-vit-base-patch32)")

args = parser.parse_args()

# Page configuration
st.set_page_config(
    page_title="Vector Search CLIP",
    layout="wide",
)

# Require authentication before loading the app
if load_login():
    # User is authenticated, load the home page
    load_home()



