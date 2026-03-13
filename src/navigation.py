import streamlit as st
from pathlib import Path
from src.image_search import ImageSearchApp
from src.rebuild_db_on_deploy import check_and_fix_paths
from src.auth import render_logout_button

def load_navigation_css():
    # Initialize app if not already done
    if 'app' not in st.session_state:
        # Fix any Windows-style backslashes in the database (for cross-platform compatibility)
        try:
            check_and_fix_paths()
        except Exception as e:
            st.warning(f"Could not fix database paths: {e}")

        embedded_data = "embedded_data"
        model_name = "openai/clip-vit-base-patch32"
        st.session_state.app = ImageSearchApp(embedded_data=embedded_data, model_name=model_name)
    
    app = st.session_state.app

    css_file = Path(__file__).parent.parent / "src" / "style" / "styles.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Display logged-in user info
    if st.session_state.get('authenticated') and st.session_state.get('user'):
        user = st.session_state['user']
        st.sidebar.success(f"👤 Logged in as: **{user['full_name']}**")
        st.sidebar.caption(f"Role: {user['role']}")
        render_logout_button()
        st.sidebar.markdown("---")

    # Sidebar navigation
    st.sidebar.markdown("## Navigation")
    st.sidebar.page_link("pages/home.py", label="Home")
    st.sidebar.page_link("pages/image_search.py", label="Image Search")
    st.sidebar.page_link("pages/text_search.py", label="Text Search")
    st.sidebar.page_link("pages/manage_images.py", label="Manage Images")
    with st.sidebar:
        st.markdown("---")
        st.metric("Total Images", len(app.image_paths))
    
    # Spacer to push footer to bottom
    st.sidebar.markdown("<div style='flex: 1;'></div>", unsafe_allow_html=True)
    
    with st.sidebar:   
        st.markdown("""
                    <footer>
                        <p>By Furquan Mobeen</p>
                    </footer>
                    """, unsafe_allow_html=True)

