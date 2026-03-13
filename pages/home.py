import streamlit as st
from src.navigation import load_navigation_css
from src.auth import is_authenticated


def load_home():
    # Check authentication
    if not is_authenticated():
        st.warning("⚠️ Please login to access this page")
        st.page_link("app.py", label="← Go to Login")
        st.stop()

    load_navigation_css()
    app = st.session_state.app
    
    # Home Page UI
    st.markdown("<h1 class='page-title'>CLIP Vector Search</h1>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("## Image Search")
        st.markdown("""
        Upload an image to find visually similar images in your database.
        Perfect for finding duplicates, similar styles, or related content.
        """)
        st.page_link("pages/image_search.py", label="Go to Image Search →")

    with col2:
        st.markdown("## Text Search")
        st.markdown("""
        Describe what you're looking for in words and find matching images.
        Uses AI to understand semantic meaning, not just keywords.
        """)
        st.page_link("pages/text_search.py", label="Go to Text Search →")

    with col3:
        st.markdown("## Manage Your Images")
        st.markdown("""
        Browse your image database, edit metadata, and manage your collection.
        """)
        st.page_link("pages/manage_images.py", label="Go to Manage Images →")
        
if __name__ == "__main__":
    load_home()
