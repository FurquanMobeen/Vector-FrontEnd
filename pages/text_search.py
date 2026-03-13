import streamlit as st
from PIL import Image
from src.navigation import load_navigation_css
from src.auth import is_authenticated

st.set_page_config(page_title="Text Search", layout="wide")

# Require authentication
if not is_authenticated():
    st.warning("⚠️ Please login to access this page")
    st.page_link("app.py", label="← Go to Login")
    st.stop()

load_navigation_css()
app = st.session_state.app

st.markdown("#### CLIP Vector Search\n # TEXT SEARCH")
st.markdown("---")

# Initialize pagination state
if "text_current_page" not in st.session_state:
    st.session_state.text_current_page = 0

RESULTS_PER_PAGE = 9

st.markdown("## Search by Text")
col1, col2 = st.columns([1, 2])
with col1:
    
    st.markdown("#### Insert Text")
    query_text = st.text_area(
        "Text query",
        placeholder="Enter a description (e.g., 'golden retriever', 'beach sunset', 'pizza')...",
        height=200,
        label_visibility="collapsed"
    )

    # Clear results if query is removed
    if not query_text and "text_search_results" in st.session_state:
        del st.session_state.text_search_results
    
    if st.button("Search by Text", use_container_width=True, key="search_btn_text"):
        if query_text:
            with st.spinner("Searching..."):
                results = app.text_search_and_format(query_text, 100)
                st.session_state.text_search_results = results
                st.session_state.text_current_page = 0  # Reset to first page
                st.rerun()
        else:
            st.error("Please enter a text")

with col2:
    st.markdown("#### Similar Images")
    if "text_search_results" in st.session_state and st.session_state.text_search_results:
        results = st.session_state.text_search_results
        current_page = st.session_state.text_current_page

        # Calculate start and end indices for current page
        start_idx = current_page * RESULTS_PER_PAGE
        end_idx = min(start_idx + RESULTS_PER_PAGE, len(results))
        page_results = results[start_idx:end_idx]

        # Display results in a grid
        cols = st.columns(3)
        for idx, result in enumerate(page_results):
            img_path = result[0] if isinstance(result, (list, tuple)) else result
            with cols[idx % 3]:
                try:
                    # Load image with PIL for better compatibility on Streamlit Cloud
                    img = Image.open(img_path)
                    st.image(img, use_container_width=True)
                except Exception as e:
                    st.error(f"Error loading image: {e}")
    else:
        st.info("Enter a text query and click 'Search by Text' to see results")

    if "text_search_results" in st.session_state and st.session_state.text_search_results:
        total_results = len(st.session_state.text_search_results)
        total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        current_page = st.session_state.text_current_page

        col_prev, col_info, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.button("← Prev", disabled=(current_page == 0), use_container_width=True, key="text_prev"):
                st.session_state.text_current_page -= 1
                st.rerun()

        with col_info:
            st.markdown(f"<p class='text-center'><strong>Page {current_page + 1} / {total_pages}</strong></p>", unsafe_allow_html=True)

        with col_next:
            if st.button("Next →", disabled=(current_page >= total_pages - 1), use_container_width=True, key="text_next"):
                st.session_state.text_current_page += 1
                st.rerun()

