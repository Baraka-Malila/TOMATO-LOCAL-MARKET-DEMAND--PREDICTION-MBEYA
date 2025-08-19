#!/bin/bash
# Weekly Model Retraining Script

set -e  

LOG_FILE="/home/cyberpunk/LOCAL-MARKET-MBEYA-NYANYA/automation/retrain.log"
DATA_REPO="https://github.com/yBaraka-Malila/tomato-market-data.git"
PROJECT_DIR="/home/cyberpunk/LOCAL-MARKET-MBEYA-NYANYA"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting weekly model retraining..."

# Step 1: Pull latest data from GitHub
log "Pulling latest data from GitHub..."
cd "$PROJECT_DIR"

if [ -d "market_data_repo" ]; then
    cd market_data_repo
    git pull origin main
else
    git clone "$DATA_REPO" market_data_repo
    cd market_data_repo
fi

# Copy new data to project
cp data/combined_file.csv ../data/
log "Data updated successfully"

# Step 2: Notify for Colab training
log "🚨 MANUAL STEP REQUIRED:"
log "1. Open your Google Colab notebook"
log "2. Upload the updated data file"
log "3. Run all cells to train the model"
log "4. Download the 4 .pkl files"
log "5. Copy them to $PROJECT_DIR/models/"

# Step 3: Wait for model files and restart Django
read -p "Press Enter after completing Colab training and copying model files..."

# Step 4: Restart Django
log "Restarting Django..."
cd "$PROJECT_DIR/nyanya_backend"


pkill -f "manage.py runserver" || true
sleep 2


nohup python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &

log "Django restarted with new model"
log "Weekly retraining completed successfully!"

# Step 5: Test the API
sleep 5
curl -s -X POST http://localhost:8000/api/predictions/run/ \
  -H "Content-Type: application/json" \
  -d '{"week": 33, "rainfall_mm": 80, "temperature_c": 25}' | jq .

log "API test completed"
