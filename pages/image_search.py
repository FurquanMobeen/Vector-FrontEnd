import streamlit as st
from PIL import Image
from src.navigation import load_navigation_css
from src.auth import is_authenticated

st.set_page_config(page_title="CLIP Vector Search", layout="wide")

# Require authentication
if not is_authenticated():
    st.warning("⚠️ Please login to access this page")
    st.page_link("app.py", label="← Go to Login")
    st.stop()

load_navigation_css()
app = st.session_state.app

st.markdown("#### CLIP Vector Search\n # IMAGE SEARCH")
st.markdown("---")

# Initialize pagination state
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
    
RESULTS_PER_PAGE = 9

st.markdown("## Search by Image")
col1, col2 = st.columns([1, 2])
with col1:
    
    st.markdown("#### Upload Image")
    
    query_image = st.file_uploader(
        "Upload image",
        type=["jpg", "jpeg", "png", "gif", "bmp"],
        label_visibility="collapsed"
    )

    # Clear results if image is removed
    if not query_image and "search_results" in st.session_state:
        del st.session_state.search_results
        st.session_state.rotation_angle = 0

    if query_image:
        # Initialize rotation state
        if "rotation_angle" not in st.session_state:
            st.session_state.rotation_angle = 0

        # Load and rotate image
        img = Image.open(query_image)
        if st.session_state.rotation_angle != 0:
            img = img.rotate(st.session_state.rotation_angle, expand=True)

        st.image(img, caption="Query Image")

        # Rotation controls
        col_rot1, col_rot2, col_rot3 = st.columns(3)

        with col_rot1:
            if st.button("↺ 90°", use_container_width=True, key="rotate_left"):
                st.session_state.rotation_angle = (st.session_state.rotation_angle + 90) % 360
                st.rerun()

        with col_rot2:
            if st.button("Reset", use_container_width=True, key="rotate_reset"):
                st.session_state.rotation_angle = 0
                st.rerun()

        with col_rot3:
            if st.button("↻ 90°", use_container_width=True, key="rotate_right"):
                st.session_state.rotation_angle = (st.session_state.rotation_angle - 90) % 360
                st.rerun()

        if st.button("Search by Image", use_container_width=True, key="search_btn_img"):
            with st.spinner("Searching..."):
                # Use the rotated image for search
                search_img = Image.open(query_image)
                if st.session_state.rotation_angle != 0:
                    search_img = search_img.rotate(st.session_state.rotation_angle, expand=True)

                # Get more results for pagination (e.g., 100 results)
                results = app.search_and_format(search_img, 100)
                st.session_state.search_results = results
                st.session_state.current_page = 0  # Reset to first page
                st.rerun()

with col2:
    st.markdown("#### Similar Images")
    if "search_results" in st.session_state and st.session_state.search_results:
        results = st.session_state.search_results
        current_page = st.session_state.current_page

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
        st.info("Upload an image and click 'Search by Image' to see results")
    
    if "search_results" in st.session_state and st.session_state.search_results:
        total_results = len(st.session_state.search_results)
        total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        current_page = st.session_state.current_page

        col_prev, col_info, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.button("← Prev", disabled=(current_page == 0), use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()

        with col_info:
            st.markdown(f"<p class='text-center'><strong>Page {current_page + 1} / {total_pages}</strong></p>", unsafe_allow_html=True)

        with col_next:
            if st.button("Next →", disabled=(current_page >= total_pages - 1), use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()

