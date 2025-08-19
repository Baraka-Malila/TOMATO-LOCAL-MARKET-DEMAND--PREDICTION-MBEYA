import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path
import time

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
if 'simulation_playing' not in st.session_state:
    st.session_state.simulation_playing = False
if 'simulation_frame' not in st.session_state:
    st.session_state.simulation_frame = 0

def load_html_page():
    """Load and modify the HTML landing page to hide the original Get Started button"""
    html_file = Path(__file__).parent / "home.html"
    
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Hide the HTML "Get Started" button instead of removing it (to preserve layout)
        modified_html = html_content.replace(
            '<a class="cta" href="http://localhost:8501/"> Get Started</a>',
            '<a class="cta" href="http://localhost:8501/" style="visibility: hidden; pointer-events: none;"> Get Started</a>'
        )
        
        # Also hide from mobile menu if exists
        modified_html = modified_html.replace(
            '<a href="#contact">Get Started</a>',
            '<a href="#contact" style="visibility: hidden; pointer-events: none;">Get Started</a>'
        )
        
        return modified_html
    else:
        return """
        <div style="text-align: center; padding: 50px;">
            <h1>HTML file not found</h1>
            <p>Please make sure home.html is in the same directory as this script</p>
        </div>
        """

def show_landing_page():
    """Display the landing page with themed navigation buttons"""
    # Full-screen HTML display (ONLY for landing page - not global)
    st.markdown("""
    <style>
    /* Landing page ONLY: Remove all Streamlit styling */
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
    
    /* Make iframe full screen ONLY on landing */
    iframe {
        border: none !important;
        width: 100vw !important;
        height: 100vh !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        z-index: 999 !important;
    }
    
    /* Themed navigation buttons positioned above iframe */
    .stButton > button {
        background: linear-gradient(135deg, #6aa9ff, #6ef3c5) !important;
        color: #0b0d12 !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 20px rgba(106, 169, 255, 0.35) !important;
        backdrop-filter: blur(10px) !important;
        position: fixed !important;
        z-index: 2000 !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a98ef, #5ee3b5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(106, 169, 255, 0.45) !important;
    }
    
    /* Position button exactly where HTML "Get Started" button was */
    .stButton:nth-of-type(1) > button {
        position: fixed !important;
        top: 18px !important;
        right: 20px !important;
        z-index: 2000 !important;
        width: 110px !important;
        height: 40px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        border-radius: 25px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display HTML
    html_content = load_html_page()
    components.html(html_content, height=1080, scrolling=True)
    
    # Single "Get Started" button overlay (no emoji, exact positioning)
    if st.button("Get Started", key="get_started_btn"):
        st.session_state.page = 'auth'
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
    # RESET all iframe styling - return to normal Streamlit layout
    st.markdown("""
    <style>
    /* Auth page: RESET to normal Streamlit layout */
    .main {
        padding: 2rem !important;
        max-width: 600px !important;
        margin: 0 auto !important;
        position: relative !important;
    }
    
    .main > div {
        padding: 0 !important;
        position: relative !important;
    }
    
    header[data-testid="stHeader"] {
        display: block !important;
        position: relative !important;
    }
    
    /* RESET iframe to normal behavior */
    iframe {
        position: relative !important;
        width: 100% !important;
        height: auto !important;
        z-index: auto !important;
        top: auto !important;
        left: auto !important;
        border: 1px solid #ddd !important;
    }
    
    /* RESET buttons to normal */
    .stButton > button {
        position: relative !important;
        z-index: auto !important;
        background: #ff4b4b !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: normal !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
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

def fetch_dashboard_data():
    """Fetch all dashboard data from APIs"""
    try:
        # Fetch KPI cards data
        cards_response = requests.get(f"{API_BASE_URL}/predictions/dashboard-cards/")
        cards_data = cards_response.json() if cards_response.status_code == 200 else {}
        
        # Fetch current week prediction
        current_response = requests.get(f"{API_BASE_URL}/predictions/current-week/")
        current_data = current_response.json() if current_response.status_code == 200 else {}
        
        # Fetch chart data
        chart_response = requests.get(f"{API_BASE_URL}/predictions/chart-data/")
        chart_data = chart_response.json() if chart_response.status_code == 200 else {}
        
        # Fetch simulation data
        simulation_response = requests.get(f"{API_BASE_URL}/predictions/simulate/?start=1&end=20&year=2025")
        simulation_data = simulation_response.json() if simulation_response.status_code == 200 else {}
        
        return {
            'cards': cards_data,
            'current': current_data,
            'chart': chart_data,
            'simulation': simulation_data
        }
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return {'cards': {}, 'current': {}, 'chart': {}, 'simulation': {}}

def create_demand_trend_chart(chart_data):
    """Create line chart for demand trends using native Streamlit"""
    if not chart_data or 'trend_data' not in chart_data:
        # Fallback data
        weeks = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8']
        demand_values = [65, 70, 68, 75, 72, 78, 73, 80]
    else:
        trend_data = chart_data['trend_data']
        weeks = [item['week'] for item in trend_data]
        demand_values = [item['demand_value'] * 25 for item in trend_data]  # Scale to percentage
    
    # Create DataFrame for Streamlit chart
    chart_df = pd.DataFrame({
        'Week': weeks,
        'Demand %': demand_values,
        'Forecast %': [v + 5 for v in demand_values]
    })
    
    return chart_df

def create_animation_chart(simulation_data):
    """Create ULTRA SMOOTH animated bubble chart with MANY MANY small bubbles - keep original colors"""
    if not simulation_data or 'frames' not in simulation_data:
        # Fallback data - MANY MANY traders with VERY different behaviors and sizes
        trader_names = [f"Trader_{i+1}" for i in range(150)]  # 150 traders - MORE!
        weeks = list(range(1, 26))  # 25 frames for ULTRA SMOOTH animation!
        
        df_data = []
        for week in weeks:
            for i, trader in enumerate(trader_names):
                # VERY different size categories - mostly small!
                if i < 90:  # 60% tiny traders
                    base_size = 3 + (i % 6)  # Very tiny: 3-8
                    trader_type = 'Small Trader'
                elif i < 127:  # 25% medium traders  
                    base_size = 9 + (i % 8)  # Medium: 9-16
                    trader_type = 'Medium Trader'
                elif i < 142:  # 10% large traders
                    base_size = 17 + (i % 10)  # Large: 17-26
                    trader_type = 'Large Trader'
                else:  # 5% huge traders
                    base_size = 27 + (i % 15)  # Huge: 27-41
                    trader_type = 'Major Trader'
                
                # COMPLETELY different SMOOTH movement patterns for each trader
                movement_type = i % 15  # 15 different movement patterns
                
                # Create ULTRA SMOOTH interpolated movements
                progress = (week - 1) / 24  # Smooth 0 to 1 progress over 25 frames
                
                if movement_type == 0:  # Smooth random movers
                    base_conf = 30 + (i * 0.7)
                    base_demand = 1.2 + (i % 5) * 0.4
                    # Smooth sine wave variation
                    confidence = base_conf + 15 * ((week / 5) % 1) + (i % 13 - 6) * 2
                    demand = base_demand + 0.5 * ((week / 3) % 1) + (i % 7 - 3) * 0.05
                elif movement_type == 1:  # Smooth trend followers
                    confidence = 40 + (progress * 40) + (i % 9 - 4) * 1.5
                    demand = 1.5 + (progress * 1.2) + (i % 3) * 0.3
                elif movement_type == 2:  # Smooth volatile traders
                    volatility = ((week * 0.8) % 4 - 2) / 2  # Smooth oscillation
                    confidence = 50 + volatility * 25 + (i % 17 - 8) * 2
                    demand = 2.0 + volatility * 0.6 + (i % 5) * 0.1
                elif movement_type == 3:  # Smooth conservative
                    confidence = 60 + (i % 11) * 1.2 + (progress * 10)
                    demand = 1.8 + (i % 7) * 0.08 + (progress * 0.2)
                elif movement_type == 4:  # Smooth contrarian
                    confidence = 45 + (1 - progress) * 20 + (i % 19) * 1.5
                    demand = 2.5 - (progress * 0.8) + (i % 5) * 0.15
                elif movement_type == 5:  # Smooth cyclical
                    cycle = (week * 0.6) % 6 - 3  # Smooth cycle
                    confidence = 55 + cycle * 8 + (i % 11) * 1
                    demand = 2.0 + cycle * 0.2 + (i % 3) * 0.1
                elif movement_type == 6:  # Smooth momentum
                    momentum = progress ** 1.5
                    confidence = 35 + momentum * 30 + (i % 7) * 2
                    demand = 1.3 + momentum * 0.8 + (i % 4) * 0.2
                elif movement_type == 7:  # Smooth seasonal
                    seasonal = ((week * 0.4) % 8 - 4) / 4  # Smooth season
                    confidence = 50 + seasonal * 15 + (i % 13) * 1.2
                    demand = 1.7 + seasonal * 0.3 + (i % 5) * 0.1
                elif movement_type == 8:  # Smooth news-driven
                    news_cycle = ((week * 0.7) % 6 - 3) / 3
                    confidence = 40 + news_cycle * 20 + (i % 23 - 11) * 1.5
                    demand = 1.9 + news_cycle * 0.4 + (i % 6 - 3) * 0.08
                elif movement_type == 9:  # Smooth wave pattern
                    wave = (week * 0.5) % 10 - 5  # Smooth wave
                    confidence = 45 + wave * 6 + (i % 17) * 1.8
                    demand = 2.1 + wave * 0.15 + (i % 7) * 0.12
                elif movement_type == 10:  # Smooth lag traders
                    lag_progress = max(0, progress - 0.2)  # Delayed start
                    confidence = 35 + lag_progress * 35 + (i % 31) * 1.3
                    demand = 1.4 + lag_progress * 0.9 + (i % 9 - 4) * 0.06
                elif movement_type == 11:  # Smooth jump traders
                    jump = 1 if (week % 8 > 4) else 0  # Smooth transitions
                    confidence = 45 + jump * 20 + (progress * 15) + (i % 13) * 1.5
                    demand = 1.8 + jump * 0.4 + (progress * 0.3) + (i % 5 - 2) * 0.08
                elif movement_type == 12:  # Ultra smooth operators
                    confidence = 50 + (progress * 25) + (i % 37) * 0.8
                    demand = 1.6 + (progress * 0.6) + (i % 11 - 5) * 0.04
                elif movement_type == 13:  # Smooth chaos traders
                    chaos = ((week * 1.1) % 12 - 6) / 6  # Controlled chaos
                    confidence = 35 + chaos * 18 + (i % 29) * 1.4
                    demand = 1.3 + chaos * 0.35 + (i % 13 - 6) * 0.07
                else:  # Smooth ultra volatile
                    ultra_vol = ((week * 0.9) % 8 - 4) / 4
                    confidence = 30 + ultra_vol * 25 + (i % 41) * 1.1
                    demand = 1.1 + ultra_vol * 0.7 + (i % 17 - 8) * 0.09
                
                # Smooth size variation to bubble
                size_variation = base_size + (progress * (i % 5 - 2) * 1.5) + ((week * 0.3) % 2 - 1)
                final_size = max(2, min(45, size_variation))
                
                df_data.append({
                    'week': week,
                    'trader': trader,
                    'demand_level': max(0.5, min(3.5, demand)),
                    'confidence': max(15, min(95, confidence)),
                    'volume': final_size,
                    'category': trader_type,
                    'profit': 200 + (i * 12) + (confidence * 15),
                    'movement_type': movement_type
                })
        
        df = pd.DataFrame(df_data)
    else:
        # Use REAL simulation data - CREATE MANY MANY traders with EXTREME variety and ULTRA SMOOTH movement
        frames = simulation_data['frames']
        trader_names = [f"Farm_{i+1}" for i in range(180)]  # 180 traders - EVEN MORE!
        
        # Create interpolated frames for ULTRA SMOOTH animation
        total_frames = max(20, len(frames) * 3)  # Triple the frames for smoothness
        
        # Map demand levels to numeric values
        demand_map = {'Low': 1, 'Medium': 2, 'High': 3}
        
        df_data = []
        for frame_idx in range(total_frames):
            # Interpolate between real frames
            real_frame_idx = min(len(frames) - 1, int((frame_idx / total_frames) * len(frames)))
            frame = frames[real_frame_idx]
            
            week = frame_idx + 1  # Use interpolated week
            base_confidence = frame.get('confidence', 0.85) * 100
            base_demand = demand_map.get(frame.get('predicted_demand', 'Medium'), 2)
            is_match = frame.get('match', True)
            
            # Create 180 VERY different traders with EXTREME variety and SMOOTH movement
            for i, trader in enumerate(trader_names):
                # Size distribution - MOSTLY TINY
                if i < 108:  # 60% micro traders
                    base_size = 2 + (i % 5)  # 2-6 (micro)
                    trader_type = 'Micro Farm'
                elif i < 144:  # 20% tiny traders
                    base_size = 7 + (i % 6)  # 7-12 (tiny)
                    trader_type = 'Small Farm'
                elif i < 162:  # 10% small traders
                    base_size = 13 + (i % 8)  # 13-20 (small)
                    trader_type = 'Medium Farm'
                elif i < 171:  # 5% medium traders
                    base_size = 21 + (i % 10)  # 21-30 (medium)
                    trader_type = 'Large Farm'
                elif i < 177:  # 3% large traders
                    base_size = 31 + (i % 12)  # 31-42 (large)
                    trader_type = 'Major Farm'
                else:  # 2% huge traders
                    base_size = 43 + (i % 15)  # 43-57 (huge)
                    trader_type = 'Corporate Farm'
                
                # EXTREME behavior variety - 20 different SMOOTH patterns
                behavior = i % 20
                progress = frame_idx / max(1, total_frames - 1)  # Smooth 0-1 progress
                
                # Each behavior responds VERY differently with SMOOTH interpolation
                if behavior == 0:  # Micro volatile with smooth waves
                    conf_mult = 0.5 + 0.3 * ((frame_idx * 0.4) % 4 - 2) / 2 + (i % 23 * 0.02)
                    demand_shift = 0.2 * ((frame_idx * 0.3) % 6 - 3) / 3 + (i % 17 - 8) * 0.02
                elif behavior == 1:  # Smooth trend amplifiers
                    conf_mult = 1.2 + (progress * 0.4) + 0.2 * ((frame_idx * 0.2) % 3 - 1.5) / 1.5 + (i % 11 * 0.03)
                    demand_shift = (progress * 0.6) + 0.1 * ((frame_idx * 0.25) % 4 - 2) / 2 + (i % 7 - 3) * 0.05
                elif behavior == 2:  # Smooth market rebels
                    rebel_wave = ((frame_idx * 0.35) % 8 - 4) / 4
                    conf_mult = 1.5 - (base_confidence * 0.008) + rebel_wave * 0.3 + (i % 19 * 0.015)
                    demand_shift = -(progress * 0.4) + rebel_wave * 0.2 + (i % 9) * 0.12
                elif behavior == 3:  # Smooth noise traders
                    noise = ((frame_idx * 0.6 + i * 0.3) % 10 - 5) / 5
                    conf_mult = 0.8 + noise * 0.4 + (i % 31 * 0.018)
                    demand_shift = noise * 0.25 + (i % 13 - 6) * 0.03
                elif behavior == 4:  # Smooth momentum followers
                    momentum = progress ** 1.2
                    momentum_wave = ((frame_idx * 0.28) % 5 - 2.5) / 2.5
                    conf_mult = 0.7 + momentum * 0.6 + momentum_wave * 0.2 + (i % 13 * 0.025)
                    demand_shift = momentum * 0.8 + momentum_wave * 0.15 + (i % 5 - 2) * 0.06
                elif behavior == 5:  # Smooth mean reverters
                    revert_cycle = ((frame_idx * 0.22) % 12 - 6) / 6
                    conf_mult = 1.3 - (progress * 0.3) + revert_cycle * 0.25 + (i % 21 * 0.02)
                    demand_shift = -(progress * 0.4) + revert_cycle * 0.18 + (i % 11 - 5) * 0.04
                elif behavior == 6:  # Smooth herders
                    herd_strength = 0.6 + 0.4 * ((frame_idx * 0.15) % 6 - 3) / 3
                    conf_mult = 0.9 + (8 if is_match else -6) * 0.01 * herd_strength + (i % 7 * 0.03)
                    demand_shift = (4 if is_match else -2) * 0.1 * herd_strength + (i % 3 - 1) * 0.08
                # Continue with more smooth behaviors...
                else:  # Default smooth pattern
                    smooth_var = ((frame_idx * 0.45 + i * 0.2) % 16 - 8) / 8
                    conf_mult = 0.85 + smooth_var * 0.35 + (i % 37 * 0.02)
                    demand_shift = smooth_var * 0.3 + (i % 19 - 9) * 0.025
                
                # Apply SMOOTH transformations
                final_confidence = base_confidence * conf_mult + ((i % 43 - 21) * 0.8)
                final_demand = base_demand + demand_shift + ((i % 29 - 14) * 0.03)
                
                # SMOOTH size variation based on performance and progress
                size_var = base_size * (1 + (final_confidence - 50) * 0.003) + (progress * (i % 7 - 3) * 0.5)
                final_size = max(1.5, min(60, size_var))
                
                df_data.append({
                    'week': week,
                    'trader': trader,
                    'demand_level': max(0.3, min(3.7, final_demand)),
                    'confidence': max(5, min(98, final_confidence)),
                    'volume': final_size,
                    'category': trader_type,
                    'profit': 100 + (i * 8) + (final_confidence * 12),
                    'movement_type': behavior
                })
        
        df = pd.DataFrame(df_data)
    
    # Create ULTRA SMOOTH animated bubble chart with MANY MANY SMALL BUBBLES
    fig = px.scatter(
        df,
        x='demand_level',
        y='confidence',
        size='volume',
        color='category',
        animation_frame='week',
        hover_name='trader',
        hover_data={
            'profit': ':,',
            'volume': ':.1f',
            'demand_level': ':.2f',
            'confidence': ':.1f',
            'movement_type': True
        },
        size_max=25,  # Smaller max size for more bubbles
        range_x=[0.2, 3.8],
        range_y=[0, 100],
        # NO TITLE - removed as requested
        color_discrete_sequence=px.colors.qualitative.Pastel  # Keep original colors!
    )
    
    # Update layout for clean appearance - NO TITLE
    fig.update_layout(
        xaxis_title='Demand Level',
        yaxis_title='Confidence %',
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3],
            ticktext=['Low', 'Medium', 'High']
        ),
        showlegend=True,
        legend=dict(
            title="Farm Size", 
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(size=8)  # Even smaller legend
        ),
        height=350,
        margin=dict(l=0, r=0, t=15, b=0),  # Minimal top margin
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # ULTRA SMOOTH animation settings - KEY FOR SMOOTHNESS!
    if hasattr(fig.layout, 'updatemenus') and fig.layout.updatemenus:
        fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 400  # Faster frames
        fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 600  # Longer smooth transitions
        fig.layout.updatemenus[0].buttons[0].args[1]['transition']['easing'] = 'cubic-in-out'  # Smooth easing curve
    
    return fig

def create_simulation_data(simulation_data, current_frame=0):
    """Process simulation data for charts"""
    if not simulation_data or 'frames' not in simulation_data:
        return {
            'accuracy': 85,
            'current_week': 1,
            'prediction': 'Medium',
            'actual': 'Medium',
            'confidence': 85,
            'match': True
        }
    
    frames = simulation_data['frames']
    if current_frame < len(frames):
        frame = frames[current_frame]
        return {
            'accuracy': len([f for f in frames[:current_frame+1] if f.get('match', False)]) / len(frames[:current_frame+1]) * 100 if current_frame >= 0 else 85,
            'current_week': frame.get('week', 1),
            'prediction': frame.get('predicted_demand', 'Medium'),
            'actual': frame.get('actual_demand', 'Medium'),
            'confidence': frame.get('confidence', 0.85) * 100,
            'match': frame.get('match', True)
        }
    
    return {'accuracy': 85, 'current_week': 1, 'prediction': 'Medium', 'actual': 'Medium', 'confidence': 85, 'match': True}

def show_dashboard():
    """Display clean dashboard matching the design"""
    # Clean dashboard styling matching landing page theme
    st.markdown("""
    <style>
    /* Dashboard using landing page theme */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        background-color: #f5f6fa;
    }
    
    /* Header bar */
    .header-bar {
        background: #f8f9fa;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        border-bottom: 1px solid rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .logo-circle {
        width: 35px;
        height: 35px;
        background: linear-gradient(135deg, #6aa9ff, #6ef3c5);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #0b0d12;
    }
    
    /* Breadcrumb */
    .breadcrumb {
        margin: 0 20px 15px 20px;
        font-size: 12px;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
    }
    
    /* KPI Cards - smaller and clean */
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin: 0 20px 20px 20px;
    }
    
    .kpi-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 5px;
    }
    
    .kpi-change {
        font-size: 12px;
        font-weight: 500;
        color: #6b7280;
    }
    
    .kpi-change.positive {
        color: #10b981;
    }
    
    .kpi-change.negative {
        color: #ef4444;
    }
    
    /* Middle section */
    .middle-section {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 20px;
        margin: 0 20px 20px 20px;
    }
    
    /* Status cards */
    .status-cards {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    
    .status-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .status-icon {
        width: 35px;
        height: 35px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }
    
    .status-icon.health { background: #ef4444; color: white; }
    .status-icon.weather { background: #10b981; color: white; }
    
    .status-text h4 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
        color: #1f2937;
    }
    
    .status-text p {
        margin: 0;
        font-size: 12px;
        color: #6b7280;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chart-title {
        font-size: 14px;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Tips container */
    .tips-container {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    .tips-header {
        background: #1f2937;
        color: white;
        padding: 12px 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .tips-content {
        padding: 15px;
    }
    
    .tip-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .tip-item:last-child {
        border-bottom: none;
    }
    
    .tip-icon {
        width: 30px;
        height: 30px;
        background: #f8fafc;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }
    
    .tip-text {
        font-size: 12px;
        color: #374151;
        font-weight: 500;
        line-height: 1.4;
    }
    
    /* Bottom section */
    .bottom-section {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 20px;
        margin: 0 20px;
    }
    
    /* Download section */
    .download-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .download-circle {
        width: 60px;
        height: 60px;
        background: #1f2937;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px auto;
        color: white;
        font-size: 18px;
    }
    
    .download-text {
        font-size: 12px;
        font-weight: 600;
        color: #1f2937;
        text-transform: uppercase;
    }
    
    /* Simulation placeholder */
    .simulation-container {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    .simulation-header {
        background: #1f2937;
        color: white;
        padding: 12px 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .simulation-content {
        background: #4ade80;
        height: 200px;
        padding: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #1f2937;
        font-weight: 600;
    }
    
    /* Reset Streamlit button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6aa9ff, #6ef3c5) !important;
        color: #0b0d12 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header bar
    st.markdown("""
    <div class="header-bar">
        <div class="logo-section">
            <div class="logo-circle">T</div>
            <span style="font-weight: bold; color: #1f2937;">TOMATO MARKET PREDICTION DASHBOARD - MBEYA REGION</span>
        </div>
        <div style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 14px; color: #6b7280;">🔔</span>
            <span style="font-size: 14px; color: #6b7280;">❓</span>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 28px; height: 28px; background: #ef4444; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 11px; font-weight: bold;">FM</div>
                <span style="font-size: 12px; color: #1f2937; font-weight: 500;">FARMER MBEYA</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Breadcrumb
    st.markdown('<div class="breadcrumb">HOME > DASHBOARD</div>', unsafe_allow_html=True)
    
    # Logout button (small, in corner)
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("Logout", key="logout_btn"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = 'landing'
            st.rerun()
    
    # Fetch data
    data = fetch_dashboard_data()
    
    # Extract real data for KPI cards
    cards_data = data.get('cards', {})
    current_data = data.get('current', {})
    
    # Card 1: Model Accuracy (from API)
    model_accuracy = cards_data.get('model_performance', {}).get('value', '85%')
    accuracy_change = cards_data.get('model_performance', {}).get('change', '+2.6%')
    
    # Card 2: Current Week Demand (from current-week API)
    current_demand = current_data.get('predicted_demand', 'MEDIUM')
    demand_confidence = current_data.get('confidence_percentage', '85%')
    
    # Card 3: Weekly Predictions (repurposed as Market Activity)
    weekly_predictions = cards_data.get('weekly_predictions', {}).get('value', '12')
    weekly_change = cards_data.get('weekly_predictions', {}).get('change', '+5.2%')
    
    # Card 4: High Demand Weeks (repurposed as Opportunities)
    high_demand_weeks = cards_data.get('high_demand_weeks', {}).get('value', '5')
    opportunity_change = cards_data.get('high_demand_weeks', {}).get('change', '+8.3%')
    
    # Determine trend classes
    accuracy_trend = "positive" if "+" in accuracy_change else "negative"
    weekly_trend = "positive" if "+" in weekly_change else "negative"
    opportunity_trend = "positive" if "+" in opportunity_change else "negative"
    
    # Top KPI Cards Row with Real Data (no icons)
    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-label">PREDICTION ACCURACY</div>
            <div class="kpi-value">{model_accuracy}</div>
            <div class="kpi-change {accuracy_trend}">{accuracy_change} SINCE LAST MONTH</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">THIS WEEK DEMAND</div>
            <div class="kpi-value">{current_demand}</div>
            <div class="kpi-change positive">{demand_confidence} CONFIDENCE</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">MARKET ACTIVITY</div>
            <div class="kpi-value">{weekly_predictions}</div>
            <div class="kpi-change {weekly_trend}">{weekly_change} SINCE LAST MONTH</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">OPPORTUNITIES</div>
            <div class="kpi-value">{high_demand_weeks}</div>
            <div class="kpi-change {opportunity_trend}">{opportunity_change} POTENTIAL GAIN</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Middle Section
    st.markdown("""
    <div class="middle-section">
        <div class="status-cards">
            <div class="status-card">
                <div class="status-icon health">♥</div>
                <div class="status-text">
                    <h4>HEALTH CARE</h4>
                    <p>Current status</p>
                </div>
            </div>
            <div class="status-card">
                <div class="status-icon weather">☁</div>
                <div class="status-text">
                    <h4>WEATHER UPDATES</h4>
                    <p>Current conditions</p>
                </div>
            </div>
            <div class="download-card">
                <div class="download-circle">↓</div>
                <div class="download-text">UPDATES</div>
            </div>
        </div>
        <div class="chart-container">
            <div class="chart-title">DEMAND & FORECAST PERCENTAGE</div>
            <div style="padding: 40px; text-align: center; color: #6b7280;">
                Chart area - will be integrated later
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bottom Section - Tips and Simulation side by side
    st.markdown("""
    <div style="display: grid; grid-template-columns: 280px 1fr; gap: 20px; margin: 0 20px;">
        <div class="tips-container">
            <div class="tips-header">TIPS OF THE WEEK</div>
            <div class="tips-content">
                <div class="tip-item">
                    <div class="tip-icon">💡</div>
                    <div class="tip-text">Plant tomatoes during dry season for better yields</div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">🌱</div>
                    <div class="tip-text">Use organic fertilizers to improve soil health</div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">💧</div>
                    <div class="tip-text">Water early morning to reduce disease risk</div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">📈</div>
                    <div class="tip-text">Monitor market prices weekly for best selling time</div>
                </div>
            </div>
        </div>
        <div class="simulation-container">
            <div class="simulation-header">MARKET SIMULATION</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create and display the animated bubble chart INSIDE the simulation container
    simulation_fig = create_animation_chart(data.get('simulation', {}))
    st.plotly_chart(
        simulation_fig,
        use_container_width=True,
        key="simulation_chart"
    )

def show_full_dashboard():
    """Redirect to main dashboard - no longer needed"""
    st.session_state.page = 'dashboard'
    st.rerun()

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
