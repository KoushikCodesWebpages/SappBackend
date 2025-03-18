#!/bin/bash

set -e  # Stop script on any error

# Define colors for output
BLUE='\033[94m'
GREEN='\033[92m'
RED='\033[91m'
RESET='\033[0m'

# API URLs
UPLOAD_CSV_URL="http://localhost:8000/upload-excel-signup/"
LOGIN_URL="http://localhost:8000/login/"

# CSV files
CSV_FILES=(
    "general/data/FacultySignup.csv"
    "general/data/StudentSignup.csv"
    "general/data/SO_Admin.csv"
)

# User credentials
declare -A USERS
USERS["Student"]="student1@student.com password123 student"
USERS["Faculty"]="faculty1@school.com password123 faculty"
USERS["SO_Admin"]="admin1@example.com securepassword1 so_admin"

# Function to clean migrations
clean_migrations() {
    echo "🧹 Cleaning migrations..."
    for folder in "accounts/migrations" "features/migrations"; do
        if [ -d "$folder" ]; then
            find "$folder" -type f ! -name "__init__.py" -delete
            find "$folder" -type d -name "__pycache__" -exec rm -rf {} +
        fi
    done
    echo "✅ Migrations cleaned."
}

# Function to delete the database
delete_db() {
    DB_PATH="db.sqlite3"
    if [ -f "$DB_PATH" ]; then
        rm "$DB_PATH"
        echo "✅ Database deleted."
    else
        echo "⚠️ Database file not found, skipping."
    fi
}

# Function to run Django migrations
run_migrations() {
    echo "▶️ Running migrations..."
    python manage.py makemigrations
    python manage.py migrate
    echo "✅ Migrations completed."
}

# Function to upload CSV files sequentially
upload_csv() {
    for file in "${CSV_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "📤 Uploading $file..."
            response=$(curl -s -X POST -F "file=@$file" "$UPLOAD_CSV_URL")
            echo "✅ Response: $response"
        else
            echo "⚠️ File $file not found, skipping."
        fi
    done
}

# Function to login and get tokens
login_and_get_tokens() {
    for role in "${!USERS[@]}"; do
        read -r email password role_name <<< "${USERS[$role]}"
        
        echo "🔑 Logging in as $role..."
        response=$(curl -s -X POST "$LOGIN_URL" \
            -H "Content-Type: application/json" \
            -d "{\"email\": \"$email\", \"password\": \"$password\", \"role\": \"$role_name\"}")
        
        access_token=$(echo "$response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        
        if [ -n "$access_token" ]; then
            case $role in
                "Student") color=$BLUE ;;
                "Faculty") color=$GREEN ;;
                "SO_Admin") color=$RED ;;
                *) color=$RESET ;;
            esac
            echo -e "${color}🔹 $role Token: $access_token${RESET}"
        else
            echo "❌ Failed to get token for $role. Response: $response"
        fi
    done
}

# 🚀 Execute steps
clean_migrations
delete_db
run_migrations
sleep 2

# Start the Django server in the background
echo "🚀 Starting Django server..."
python manage.py runserver &  
SERVER_PID=$!  # Capture the server's process ID
sleep 5  # Give it time to start

# Proceed with uploading CSVs and logging in
upload_csv
login_and_get_tokens

echo "✅ Setup complete!"
echo "🖥️ Server is running... (Press Ctrl + C to stop)"

# Keep the server running in the foreground
wait $SERVER_PID
