# API Integration Guide: Postman Testing & Streamlit Integration

This comprehensive guide covers how to test your Django APIs with Postman and integrate them into Streamlit applications for data visualization and interaction.

## Table of Contents
- [Server Setup](#server-setup)
- [API Endpoints Overview](#api-endpoints-overview)
- [Postman Testing Guide](#postman-testing-guide)
- [Streamlit Integration](#streamlit-integration)
- [Data Extraction for Visuals](#data-extraction-for-visuals)
- [Error Handling](#error-handling)

---

## Server Setup

### Starting the Django Server
```bash
cd /home/cyberpunk/LOCAL-MARKET-MBEYA-NYANYA/nyanya_backend
python manage.py runserver 0.0.0.0:8000
```

**Base URL:** `http://localhost:8000` or `http://your-server-ip:8000`

**API Documentation:** Visit `http://localhost:8000/` for interactive Swagger docs

---

## API Endpoints Overview

### 1. Dashboard Cards - `/api/predictions/dashboard-cards/`
**Purpose:** Get metrics for dashboard cards (Total Predictions, Weekly Stats, Model Performance, High Demand Weeks)

### 2. Current Week Prediction - `/api/predictions/current-week/`
**Purpose:** Get current week's demand prediction with confidence score

### 3. Chart Data - `/api/predictions/chart-data/`
**Purpose:** Historical data for trend charts and demand distribution

### 4. Simulation - `/api/predictions/simulate-weeks/`
**Purpose:** Interactive week-by-week simulation data

### 5. Market History - `/api/market-data/history/`
**Purpose:** Raw historical market data with filtering options

---

## Postman Testing Guide

### Setting Up Postman

1. **Download Postman:** [https://www.postman.com/downloads/](https://www.postman.com/downloads/)
2. **Create New Collection:** Name it "Tomato Market API"
3. **Set Base URL Variable:**
   - Click "Environment" → "Add" → Name: "Local Dev"
   - Add variable: `base_url` = `http://localhost:8000`

### Testing Each Endpoint

#### 1. Dashboard Cards API

**Request Setup:**
```
Method: GET
URL: {{base_url}}/api/predictions/dashboard-cards/
Headers: Content-Type: application/json
```

**Expected Response:**
```json
{
    "total_predictions": {
        "value": "1,234",
        "change": "+12%",
        "trend": "up",
        "label": "TOTAL PREDICTIONS"
    },
    "weekly_predictions": {
        "value": "45",
        "change": "+8%",
        "trend": "up",
        "label": "THIS WEEK"
    },
    "model_performance": {
        "value": "87%",
        "change": "+2.6%",
        "trend": "up",
        "label": "ACCURACY"
    },
    "high_demand_weeks": {
        "value": "23",
        "change": "+5.8%",
        "trend": "up",
        "label": "HIGH DEMAND"
    }
}
```

#### 2. Current Week Prediction API

**Request Setup:**
```
Method: GET
URL: {{base_url}}/api/predictions/current-week/
```

**Expected Response:**
```json
{
    "week": 33,
    "predicted_demand": "High",
    "confidence": 0.87,
    "status_color": "red",
    "confidence_percentage": "87%"
}
```

#### 3. Chart Data API

**Request Setup:**
```
Method: GET
URL: {{base_url}}/api/predictions/chart-data/
```

**Expected Response:**
```json
{
    "trend_data": [
        {
            "week": "W1",
            "demand_level": "Medium",
            "demand_value": 2,
            "rainfall": 75.50,
            "temperature": 23.2
        }
    ],
    "demand_distribution": {
        "High": 4,
        "Medium": 6,
        "Low": 2
    },
    "total_weeks": 12
}
```

#### 4. Simulation API

**Request Setup:**
```
Method: GET
URL: {{base_url}}/api/predictions/simulate-weeks/?start=1&end=10&year=2025
```

**Query Parameters:**
- `start`: Starting week number (default: 1)
- `end`: Ending week number (default: 20)
- `year`: Year to simulate (default: 2025)

**Expected Response:**
```json
{
    "frames": [
        {
            "week": 1,
            "month": "January",
            "predicted_demand": "Medium",
            "actual_demand": "High",
            "confidence": 0.85,
            "match": false
        }
    ],
    "total_frames": 10,
    "play_speed": 500
}
```

#### 5. Market History API

**Request Setup:**
```
Method: GET
URL: {{base_url}}/api/market-data/history/?year=2025&limit=50
```

**Query Parameters:**
- `year`: Filter by year
- `month`: Filter by month
- `limit`: Number of records (default: 100)
- `demand`: Filter by demand level (Low/Medium/High)

**Expected Response:**
```json
{
    "count": 52,
    "data": [
        {
            "id": 1,
            "week": 1,
            "year": 2025,
            "month": "January",
            "rainfall_mm": 75.50,
            "temperature_c": 23.20,
            "market_day": true,
            "school_open": true,
            "disease_alert": "Absence",
            "last_week_demand": "Medium",
            "market_demand": "High",
            "demand_trend": "Increasing",
            "created_at": "2025-01-01T10:00:00Z"
        }
    ]
}
```

### Postman Testing Tips

1. **Save Requests:** Save each request in your collection for reuse
2. **Use Variables:** Set up environment variables for different servers (dev, staging, prod)
3. **Test Scripts:** Add JavaScript tests to validate responses
4. **Export Collection:** Share your collection with team members

**Example Test Script (in Postman Tests tab):**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('week');
    pm.expect(jsonData).to.have.property('predicted_demand');
});
```

---

## Streamlit Integration

### Basic Setup

```python
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Helper function for API calls
def get_api_data(endpoint, params=None):
    """Fetch data from API endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None
```

### 1. Dashboard Cards Implementation

```python
def display_dashboard_cards():
    """Display metric cards from dashboard API"""
    
    data = get_api_data("/api/predictions/dashboard-cards/")
    if not data:
        return
    
    # Create 4 columns for cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=data['total_predictions']['label'],
            value=data['total_predictions']['value'],
            delta=data['total_predictions']['change']
        )
    
    with col2:
        st.metric(
            label=data['weekly_predictions']['label'],
            value=data['weekly_predictions']['value'],
            delta=data['weekly_predictions']['change']
        )
    
    with col3:
        st.metric(
            label=data['model_performance']['label'],
            value=data['model_performance']['value'],
            delta=data['model_performance']['change']
        )
    
    with col4:
        st.metric(
            label=data['high_demand_weeks']['label'],
            value=data['high_demand_weeks']['value'],
            delta=data['high_demand_weeks']['change']
        )

# Usage in main app
st.title("Tomato Market Dashboard")
display_dashboard_cards()
```

### 2. Current Week Prediction Display

```python
def display_current_prediction():
    """Show current week prediction with visual indicator"""
    
    data = get_api_data("/api/predictions/current-week/")
    if not data:
        return
    
    # Create columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"Week {data['week']} Prediction")
        
        # Color-coded demand level
        demand_colors = {
            'High': '#ff4444',
            'Medium': '#ffaa44', 
            'Low': '#44ff44'
        }
        
        st.markdown(
            f"<h2 style='color: {demand_colors[data['predicted_demand']]}'>"
            f"{data['predicted_demand']} Demand</h2>",
            unsafe_allow_html=True
        )
        
        st.progress(data['confidence'])
        st.caption(f"Confidence: {data['confidence_percentage']}")
    
    with col2:
        # Create gauge chart for confidence
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = data['confidence'] * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Confidence"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

# Usage
display_current_prediction()
```

### 3. Trend Charts from Chart Data API

```python
def display_trend_charts():
    """Create trend charts from chart data API"""
    
    data = get_api_data("/api/predictions/chart-data/")
    if not data:
        return
    
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(data['trend_data'])
    
    # Demand Trend Line Chart
    st.subheader("Demand Trend Over Time")
    fig = px.line(df, x='week', y='demand_value', 
                  title='Weekly Demand Levels',
                  color_discrete_sequence=['#1f77b4'])
    
    # Add demand level labels
    fig.add_scatter(x=df['week'], y=df['demand_value'], 
                   text=df['demand_level'], mode='markers+text',
                   textposition='top center')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Weather Data Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_rain = px.bar(df, x='week', y='rainfall', 
                         title='Weekly Rainfall')
        st.plotly_chart(fig_rain, use_container_width=True)
    
    with col2:
        fig_temp = px.line(df, x='week', y='temperature', 
                          title='Weekly Temperature')
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Demand Distribution Pie Chart
    st.subheader("Demand Distribution")
    distribution = data['demand_distribution']
    
    fig_pie = px.pie(
        values=list(distribution.values()),
        names=list(distribution.keys()),
        title="Distribution of Demand Levels"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Usage
display_trend_charts()
```

### 4. Interactive Simulation Player

```python
def display_simulation():
    """Interactive week-by-week simulation player"""
    
    st.subheader("Week-by-Week Simulation")
    
    # Simulation controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_week = st.number_input("Start Week", 1, 52, 1)
    with col2:
        end_week = st.number_input("End Week", 1, 52, 20)
    with col3:
        year = st.number_input("Year", 2020, 2030, 2025)
    
    # Fetch simulation data
    params = {
        'start': start_week,
        'end': end_week,
        'year': year
    }
    
    data = get_api_data("/api/predictions/simulate-weeks/", params)
    if not data:
        return
    
    frames = data['frames']
    
    if not frames:
        st.warning("No simulation data available for the selected range")
        return
    
    # Simulation player
    st.write(f"**Simulation Range:** Week {start_week} to {end_week}, {year}")
    st.write(f"**Total Frames:** {data['total_frames']}")
    
    # Frame selector
    frame_idx = st.slider("Week", 0, len(frames)-1, 0)
    current_frame = frames[frame_idx]
    
    # Display current frame
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Week", current_frame['week'])
        st.metric("Month", current_frame['month'])
    
    with col2:
        st.metric("Predicted", current_frame['predicted_demand'])
        st.metric("Actual", current_frame['actual_demand'])
    
    with col3:
        st.metric("Confidence", f"{current_frame['confidence']:.2f}")
        match_icon = "✅" if current_frame['match'] else "❌"
        st.metric("Match", match_icon)
    
    # Simulation results summary
    matches = sum(1 for frame in frames if frame['match'])
    accuracy = (matches / len(frames)) * 100
    
    st.write(f"**Simulation Accuracy:** {accuracy:.1f}% ({matches}/{len(frames)} correct)")
    
    # Auto-play simulation
    if st.button("Auto-Play Simulation"):
        import time
        placeholder = st.empty()
        
        for i, frame in enumerate(frames):
            with placeholder.container():
                st.write(f"**Week {frame['week']} ({frame['month']})**")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"Predicted: {frame['predicted_demand']}")
                    st.write(f"Actual: {frame['actual_demand']}")
                
                with col2:
                    st.write(f"Confidence: {frame['confidence']:.2f}")
                    match_text = "Match ✅" if frame['match'] else "No Match ❌"
                    st.write(match_text)
            
            time.sleep(data['play_speed'] / 1000)  # Convert ms to seconds

# Usage
display_simulation()
```

### 5. Historical Data Analysis

```python
def display_market_history():
    """Display and analyze historical market data"""
    
    st.subheader("Historical Market Data")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        year_filter = st.selectbox("Year", [2024, 2025], index=1)
    with col2:
        months = ['All', 'January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        month_filter = st.selectbox("Month", months)
    with col3:
        demand_filter = st.selectbox("Demand Level", ['All', 'Low', 'Medium', 'High'])
    
    # Build API parameters
    params = {'year': year_filter, 'limit': 100}
    if month_filter != 'All':
        params['month'] = month_filter
    if demand_filter != 'All':
        params['demand'] = demand_filter
    
    # Fetch data
    data = get_api_data("/api/market-data/history/", params)
    if not data:
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data['data'])
    
    st.write(f"**Total Records:** {data['count']}")
    
    # Data table with search/filter
    st.dataframe(
        df[['week', 'month', 'market_demand', 'rainfall_mm', 'temperature_c', 'demand_trend']],
        use_container_width=True
    )
    
    # Analysis charts
    if not df.empty:
        # Weekly demand pattern
        fig_weekly = px.histogram(df, x='market_demand', 
                                 title='Demand Level Distribution')
        st.plotly_chart(fig_weekly, use_container_width=True)
        
        # Correlation analysis
        st.subheader("Weather vs Demand Analysis")
        
        # Scatter plot: Rainfall vs Demand
        demand_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
        df['demand_numeric'] = df['market_demand'].map(demand_mapping)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_rain = px.scatter(df, x='rainfall_mm', y='demand_numeric',
                                 color='market_demand',
                                 title='Rainfall vs Demand')
            st.plotly_chart(fig_rain, use_container_width=True)
        
        with col2:
            fig_temp = px.scatter(df, x='temperature_c', y='demand_numeric',
                                 color='market_demand',
                                 title='Temperature vs Demand')
            st.plotly_chart(fig_temp, use_container_width=True)

# Usage
display_market_history()
```

---

## Data Extraction for Visuals

### Key Data Points for Each API

#### Dashboard Cards API
```python
# Extract for metric cards
cards_data = get_api_data("/api/predictions/dashboard-cards/")

# For each card: value, change, trend
total_value = cards_data['total_predictions']['value']
total_change = cards_data['total_predictions']['change']
total_trend = cards_data['total_predictions']['trend']  # 'up' or 'down'
```

#### Chart Data API
```python
# Extract for time series charts
chart_data = get_api_data("/api/predictions/chart-data/")

# For line charts
weeks = [item['week'] for item in chart_data['trend_data']]
demand_values = [item['demand_value'] for item in chart_data['trend_data']]
rainfall = [item['rainfall'] for item in chart_data['trend_data']]
temperature = [item['temperature'] for item in chart_data['trend_data']]

# For pie charts
demand_distribution = chart_data['demand_distribution']
# {'High': 4, 'Medium': 6, 'Low': 2}
```

#### Simulation API
```python
# Extract for animation/player
sim_data = get_api_data("/api/predictions/simulate-weeks/", {'start': 1, 'end': 10})

# For each frame
for frame in sim_data['frames']:
    week = frame['week']
    predicted = frame['predicted_demand']
    actual = frame['actual_demand']
    confidence = frame['confidence']
    is_correct = frame['match']
```

### Common Streamlit Patterns

```python
# Progress bars
st.progress(confidence_score)

# Color-coded metrics
if trend == 'up':
    st.metric("Total", value, delta=change, delta_color="normal")
else:
    st.metric("Total", value, delta=change, delta_color="inverse")

# Status indicators
status_color = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}[demand_level]
st.markdown(f"<span style='color: {status_color}'>{demand_level}</span>", 
            unsafe_allow_html=True)

# Data filtering
filtered_df = df[df['market_demand'] == selected_demand]
```

---

## Error Handling

### API Error Handling

```python
def safe_api_call(endpoint, params=None, default=None):
    """Safe API call with error handling"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("API request timed out. Please try again.")
        return default
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the server is running.")
        return default
    except requests.exceptions.HTTPError as e:
        st.error(f"API returned error: {e}")
        return default
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return default
```

### Streamlit Error States

```python
# Handle empty data
data = get_api_data("/api/predictions/chart-data/")
if not data or not data.get('trend_data'):
    st.warning("No chart data available. Please check if market data exists.")
    return

# Handle API down
if data is None:
    st.error("Cannot fetch data from API. Please ensure the Django server is running on port 8000.")
    st.stop()

# Handle partial data
if len(data['trend_data']) < 5:
    st.info("Limited data available. Results may not be fully representative.")
```

---

## Complete Example Application

```python
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_BASE_URL = "http://localhost:8000"

def main():
    st.set_page_config(
        page_title="Tomato Market Analytics",
        page_icon="🍅",
        layout="wide"
    )
    
    st.title("🍅 Tomato Market Analytics Dashboard")
    st.sidebar.title("Navigation")
    
    # Sidebar navigation
    page = st.sidebar.selectbox("Choose a section", [
        "Dashboard Overview",
        "Current Prediction", 
        "Historical Analysis",
        "Week Simulation",
        "API Status"
    ])
    
    # Check API connection
    if not check_api_connection():
        st.error("⚠️ Cannot connect to API. Please start the Django server.")
        st.stop()
    
    # Route to different pages
    if page == "Dashboard Overview":
        display_dashboard_cards()
        display_trend_charts()
    elif page == "Current Prediction":
        display_current_prediction()
    elif page == "Historical Analysis":
        display_market_history()
    elif page == "Week Simulation":
        display_simulation()
    elif page == "API Status":
        display_api_status()

def check_api_connection():
    """Test API connection"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/predictions/current-week/", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    main()
```

This guide provides everything you need to test your APIs with Postman and integrate them into powerful Streamlit applications. Each API endpoint is designed to provide specific data for different visualization needs, making it easy to build comprehensive dashboards and analysis tools.
