import streamlit as st
import requests
from typing import Optional, Dict

# FastAPI backend URL
BACKEND_URL = "http://localhost:8000"


def login_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user with FastAPI backend.

    Args:
        username: User's username
        password: User's password

    Returns:
        Dict with token and user info if successful, None otherwise
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=5
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
        return None


def get_current_user(token: str) -> Optional[Dict]:
    """
    Get current user info from backend using token.

    Args:
        token: JWT access token

    Returns:
        User info dict if successful, None otherwise
    """
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get('authenticated', False) and st.session_state.get('access_token') is not None


def get_auth_headers() -> Dict[str, str]:
    """Get authorization headers for API requests."""
    token = st.session_state.get('access_token')
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def logout():
    """Clear session state and logout user."""
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.user = None
    st.session_state.pop('name', None)
    st.rerun()


def render_logout_button():
    """Render logout button in sidebar."""
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
