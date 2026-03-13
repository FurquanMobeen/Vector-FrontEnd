import streamlit as st
from src.auth import login_user, is_authenticated


def load_login():
    """
    Display login form and handle authentication.

    Returns:
        True if user is authenticated, False otherwise
    """
    # Check if already authenticated
    if is_authenticated():
        return True

    # Not authenticated - show login form
    st.markdown("<h1 style='text-align: center;'>🔐 CLIP Vector Search</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Please login to continue</h3>", unsafe_allow_html=True)
    st.markdown("---")

    # Create centered login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            st.markdown("### Login")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    with st.spinner("Authenticating..."):
                        # Call backend login API
                        result = login_user(username, password)

                        if result:
                            # Store token and user info in session state
                            st.session_state.authenticated = True
                            st.session_state.access_token = result['access_token']
                            st.session_state.user = result['user']
                            st.session_state.name = result['user']['full_name']

                            st.success(f"✅ Welcome, {result['user']['full_name']}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")

    # Show info message
    st.info("💡 **Test credentials:** username: `admin`, password: `admin123`")

    return False