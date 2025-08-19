import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Tomato Market Mbeya",
    page_icon="🍅",
    layout="wide",  # Use full width
    initial_sidebar_state="collapsed"
)

# Remove Streamlit's default styling globally
st.markdown("""
<style>
/* Global Streamlit overrides */
.reportview-container {
    margin-top: 0px !important;
    padding-top: 0px !important;
}

.main .block-container {
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    padding-left: 0px !important;
    padding-right: 0px !important;
    max-width: 100% !important;
}

div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}

div[data-testid="stDecoration"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}

div[data-testid="stStatusWidget"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}

#MainMenu {
    visibility: hidden;
    height: 0%;
}

footer {
    visibility: hidden;
    height: 0%;
}
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

def load_html_page():
    """Load the HTML landing page (no modifications needed)"""
    html_file = Path(__file__).parent / "home.html"
    
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    else:
        return """
        <div style="text-align: center; padding: 50px;">
            <h1>HTML file not found</h1>
            <p>Please make sure home.html is in the same directory as this script</p>
        </div>
        """

def show_landing_page():
    """Display the landing page with themed navigation buttons"""
    # Full-screen HTML display (only for landing page)
    st.markdown("""
    <style>
    /* Landing page: Remove all Streamlit styling */
    .main {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
        width: 100vw !important;
    }
    
    .main > div {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
        width: 100vw !important;
    }
    
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    iframe {
        border: none !important;
        width: 100vw !important;
        height: 100vh !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        z-index: 999 !important;
    }
    
    /* Themed navigation buttons */
    .nav-buttons {
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        z-index: 2000 !important;
        display: flex !important;
        gap: 10px !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6aa9ff, #6ef3c5) !important;
        color: #0b0d12 !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 20px rgba(106, 169, 255, 0.35) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a98ef, #5ee3b5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(106, 169, 255, 0.45) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display HTML
    html_content = load_html_page()
    components.html(html_content, height=1080, scrolling=True)
    
    # Themed navigation buttons overlay
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Get Started", key="get_started_btn"):
            st.session_state.page = 'auth'
            st.rerun()
    with col3:
        if st.button("📊 Dashboard", key="dashboard_btn"):
            st.session_state.page = 'auth'  # Redirect to auth first
            st.rerun()

def authenticate_user(username, password):
    """Login user and get token"""
    try:
        url = f"{API_BASE_URL}/auth/login/"
        data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            return result['token'], result['user'], None
        else:
            error_data = response.json()
            return None, None, error_data
    except Exception as e:
        return None, None, {"error": str(e)}

def register_user(username, email, password, first_name="", last_name=""):
    """Register new user"""
    try:
        url = f"{API_BASE_URL}/auth/register/"
        data = {
            "username": username,
            "email": email,
            "password": password,
            "password_confirm": password,
            "first_name": first_name,
            "last_name": last_name
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 201:
            result = response.json()
            return result['token'], result['user'], None
        else:
            error_data = response.json()
            return None, None, error_data
    except Exception as e:
        return None, None, {"error": str(e)}

def show_auth_page():
    """Display authentication page - clean and simple"""
    # Reset to normal Streamlit layout (no full-screen styling)
    st.markdown("""
    <style>
    /* Auth page: Normal Streamlit layout */
    .main {
        padding: 2rem !important;
        max-width: 600px !important;
        margin: 0 auto !important;
    }
    header[data-testid="stHeader"] {
        display: block !important;
    }
    iframe {
        position: relative !important;
        width: 100% !important;
        height: auto !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #6aa9ff;">🍅 Welcome Back</h1>
        <p style="color: #9aa3b2;">Access your tomato market dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state.page = 'landing'
        st.rerun()
    
    # Auth tabs
    tab1, tab2 = st.tabs(["🔐 Login", "👤 Register"])
    
    with tab1:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login", use_container_width=True)
            
            if login_btn and username and password:
                token, user, error = authenticate_user(username, password)
                if token:
                    st.session_state.token = token
                    st.session_state.user = user
                    st.session_state.page = 'dashboard'
                    st.success(f"Welcome, {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register"):
            reg_username = st.text_input("Username*")
            reg_email = st.text_input("Email*")
            reg_password = st.text_input("Password*", type="password")
            reg_password_confirm = st.text_input("Confirm Password*", type="password")
            register_btn = st.form_submit_button("Register", use_container_width=True)
            
            if register_btn:
                if not all([reg_username, reg_email, reg_password, reg_password_confirm]):
                    st.error("Please fill all fields")
                elif reg_password != reg_password_confirm:
                    st.error("Passwords don't match")
                else:
                    token, user, error = register_user(reg_username, reg_email, reg_password)
                    if token:
                        st.session_state.token = token
                        st.session_state.user = user
                        st.session_state.page = 'dashboard'
                        st.success(f"Account created! Welcome, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("Registration failed")

def show_dashboard():
    """Display dashboard - ready for your design"""
    # Dashboard: Normal Streamlit layout
    st.markdown("""
    <style>
    /* Dashboard page: Normal layout */
    .main {
        padding: 1rem !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] {
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with logout
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <h1 style="color: #6aa9ff;">🍅 Dashboard</h1>
        <p style="color: #9aa3b2;">Welcome, {st.session_state.user['username']}!</p>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = 'landing'
            st.success("Logged out!")
            st.rerun()
    
    st.markdown("---")
    
    # Dashboard placeholder
    st.info("🎨 **Dashboard content area** - Ready for your design!")
    
    # API test (optional)
    with st.expander("🔌 API Status"):
        if st.button("Test APIs"):
            try:
                response = requests.get(f"{API_BASE_URL}/predictions/dashboard-cards/")
                if response.status_code == 200:
                    st.success("✅ APIs working!")
                    st.json(response.json())
                else:
                    st.error(f"❌ API Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")

def main():
    """Main application logic - simplified"""
    
    # Handle page navigation
    if st.session_state.page == 'landing':
        show_landing_page()
    elif st.session_state.page == 'auth':
        show_auth_page()
    elif st.session_state.page == 'dashboard':
        show_dashboard()

if __name__ == "__main__":
    main()
