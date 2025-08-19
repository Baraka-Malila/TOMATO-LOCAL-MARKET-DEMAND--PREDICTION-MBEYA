# Get dashboard cards
cards = requests.get("http://localhost:8000/api/predictions/dashboard-cards/").json()

# Get current week prediction  
current = requests.get("http://localhost:8000/api/predictions/current-week/").json()

# Get chart data
chart_data = requests.get("http://localhost:8000/api/predictions/chart-data/").json()

# Get simulation frames
simulation = requests.get("http://localhost:8000/api/predictions/simulate/?start=30&end=35").json()