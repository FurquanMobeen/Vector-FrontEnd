import streamlit as st
from pathlib import Path
from PIL import Image
from src.navigation import load_navigation_css
from src.auth import is_authenticated

st.set_page_config(page_title="Manage Images", layout="wide")

# Require authentication
if not is_authenticated():
    st.warning("⚠️ Please login to access this page")
    st.page_link("app.py", label="← Go to Login")
    st.stop()

load_navigation_css()
app = st.session_state.app

st.markdown("#### CLIP Vector Search\n # MANAGE IMAGES")
st.markdown("---")

st.markdown("## Upload Image to Database")
col1, col2 = st.columns([1, 2])

# Initialize file uploader key counter
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

with col1:
    
    st.markdown("#### Upload Image")
    
    add_image = st.file_uploader(
        "Upload image to add",
        type=["jpg", "jpeg", "png", "gif", "bmp"],
        label_visibility="collapsed",
        key=f"add_image_{st.session_state.file_uploader_key}"
    )

    if add_image:
        # Initialize rotation state for add image
        if "add_rotation_angle" not in st.session_state:
            st.session_state.add_rotation_angle = 0

        # Load and rotate image
        add_img = Image.open(add_image)
        if st.session_state.add_rotation_angle != 0:
            add_img = add_img.rotate(st.session_state.add_rotation_angle, expand=True)

        st.image(add_img, caption="Image to Add")

        # Rotation controls
        col_rot1, col_rot2, col_rot3 = st.columns(3)

        with col_rot1:
            if st.button("↺ 90°", use_container_width=True, key="add_rotate_left"):
                st.session_state.add_rotation_angle = (st.session_state.add_rotation_angle + 90) % 360
                st.rerun()

        with col_rot2:
            if st.button("Reset", use_container_width=True, key="add_rotate_reset"):
                st.session_state.add_rotation_angle = 0
                st.rerun()

        with col_rot3:
            if st.button("↻ 90°", use_container_width=True, key="add_rotate_right"):
                st.session_state.add_rotation_angle = (st.session_state.add_rotation_angle - 90) % 360
                st.rerun()

with col2:
    st.markdown("#### Image Details")

    # Initialize session state for form fields
    if "clear_add_form" not in st.session_state:
        st.session_state.clear_add_form = False

    # Clear fields if flag is set
    if st.session_state.clear_add_form:
        st.session_state.add_title = ""
        st.session_state.add_description = ""
        st.session_state.add_rotation_angle = 0
        st.session_state.clear_add_form = False

    image_title = st.text_input(
        "Title",
        placeholder="Enter a title",
        key="add_title"
    )

    image_description = st.text_area(
        "Description",
        placeholder="Enter a description",
        height=100,
        key="add_description"
    )

    if add_image:
        if image_title:
            if image_description:
                if st.button("Add Image", use_container_width=True, key="add_btn"):
                    with st.spinner("Adding image to database..."):
                        # Use the rotated image for database
                        img = Image.open(add_image)
                        if st.session_state.add_rotation_angle != 0:
                            img = img.rotate(st.session_state.add_rotation_angle, expand=True)

                        result = app.add_to_database(img, image_title, image_description, save_dir="data")
                        if "Successfully" in result:
                            st.success(result)
                            # Set flag to clear form and increment file uploader key
                            st.session_state.clear_add_form = True
                            st.session_state.file_uploader_key += 1
                            st.rerun()
                        else:
                            st.warning(result)
            else:
                st.error("Please enter a description for the image")
        else:
            st.error("Please enter a title for the image")

st.markdown("---")

st.markdown("## Select Image to Manage")
col1, col2 = st.columns([1, 2])
with col1:

    # Create dropdown choices
    image_choices = [(f"{metadata[1]} - {Path(metadata[0]).name}", metadata[0])
                    for metadata in app.get_all_images()]

    if image_choices:
        image_paths_list = [choice[1] for choice in image_choices]
        image_display_names = [choice[0] for choice in image_choices]

        # Track if user has made an active selection
        if "manage_image_selected" not in st.session_state:
            st.session_state.manage_image_selected = False
        if "selected_idx" not in st.session_state:
            st.session_state.selected_idx = 0

        with st.expander("Select Image", expanded=False):
            # Search box
            search_query = st.text_input(
                "Search images",
                placeholder="Type to filter...",
                key="image_search",
                label_visibility="collapsed"
            )

            # Filter images based on search
            if search_query:
                filtered_indices = [i for i, name in enumerate(image_display_names)
                                  if search_query.lower() in name.lower()]
            else:
                filtered_indices = list(range(len(image_choices)))

            with st.container(height=300):
                if filtered_indices:
                    # Determine default index
                    if st.session_state.selected_idx in filtered_indices:
                        default_index = filtered_indices.index(st.session_state.selected_idx)
                    else:
                        default_index = 0

                    temp_idx = st.radio(
                        "Choose an image",
                        filtered_indices,
                        format_func=lambda x: image_display_names[x],
                        key="image_dropdown",
                        label_visibility="collapsed",
                        index=default_index
                    )

                    # If selection changed, mark as actively selected
                    if temp_idx != st.session_state.selected_idx:
                        st.session_state.selected_idx = temp_idx
                        st.session_state.manage_image_selected = True
                else:
                    st.info("No images match your search.")

        # Only show image if user has actively selected one
        selected_idx = st.session_state.selected_idx if st.session_state.manage_image_selected else None
        selected_image_path = image_paths_list[selected_idx] if selected_idx is not None else None

        if st.button("Refresh List", use_container_width=True):
            st.session_state.manage_image_selected = False
            st.rerun()

        if selected_image_path:
            st.markdown("---")
            st.markdown("#### Edit Metadata")

            # Load current metadata
            metadata = app.image_metadata.get(selected_image_path, {})
            current_title = metadata.get("title", "")
            current_description = metadata.get("description", "")

            edit_title = st.text_input(
                "Title",
                value=current_title,
                placeholder="Enter new title..."
            )

            edit_description = st.text_area(
                "Description",
                value=current_description,
                placeholder="Enter new description...",
                height=100
            )

            if st.button("Update Metadata", use_container_width=True, key="update_btn"):
                with st.spinner("Updating metadata..."):
                    result = app.update_metadata(selected_image_path, edit_title, edit_description)
                    st.success(result)
                    st.rerun()

            st.markdown("---")
            st.markdown("#### Delete Image")
            st.warning("**Warning**: This will remove the image from the database and delete it from disk.")

            if st.button("Delete from Database", use_container_width=True, key="delete_btn"):
                with st.spinner("Deleting..."):
                    result = app.delete_from_database(selected_image_path)
                    if "successfully" in result.lower() or "deleted" in result.lower():
                        st.success(result)
                        st.session_state.manage_image_selected = False  # Clear selection
                    else:
                        st.warning(result)
                    st.rerun()

    else:
        st.info("No images in database yet. Add some images from the Image Search page!")

with col2:
    st.markdown("#### Preview")

    if image_choices and selected_image_path:
        try:
            # Load image with PIL for better compatibility on Streamlit Cloud
            img = Image.open(selected_image_path)
            st.image(img, caption="Selected Image")

            metadata = app.image_metadata.get(selected_image_path, {})
            current_title = metadata.get("title", "")
            current_description = metadata.get("description", "")

            info_text = f"""
                **Title**: {current_title}\n
                **Description**: {current_description}\n
                """
            st.info(info_text)
        except Exception as e:
            st.error(f"Could not load image: {e}")
    elif image_choices:
        st.info("Select an image to view preview")

    st.markdown("---")
    st.markdown("### Export Metadata")
    
    # Export scope selection
    export_scope = st.radio(
        "Export scope",
        ["All Images", "Selected Image Only"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if export_scope == "All Images":
        st.markdown("Export all image metadata to a JSON file for backup or external use.")
    else:
        st.markdown("Export metadata for the currently selected image only.")
        
    # Disable export if "Selected Image Only" is chosen but no image is selected
    export_disabled = (export_scope == "Selected Image Only" and not selected_image_path)
    
    if st.button("Export to JSON", use_container_width=True, key="export_btn", disabled=export_disabled):
        with st.spinner("Exporting..."):
            import json
            if export_scope == "All Images":
                json_data = app.export_metadata_json()
                download_filename = "all_metadata.json"
            else:  # Selected Image Only
                metadata = app.image_metadata.get(selected_image_path, {})
                json_data = json.dumps({selected_image_path: metadata}, indent=2)
                current_title = metadata.get("title", "Untitled")
                # Sanitize filename
                sanitized_title = current_title.replace('/', '_').replace('\\', '_')
                download_filename = f"{sanitized_title}.json"
            
            st.text_area(
                "Exported JSON Data",
                value=json_data,
                height=300,
                disabled=True
            )
            
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=download_filename,
                mime="application/json",
                use_container_width=True
            )
            st.success("Metadata exported!")
