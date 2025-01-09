#!/bin/bash

# Path to your bot script
BOT_SCRIPT="FTCScout.py"
LOG_FILE="ftcscout.log"
VENV_DIR="venv"  # Directory for the virtual environment
BRANCH="main-dev"  # The branch to pull from

# Function to install pip3 if not already installed
install_pip() {
    if ! command -v pip3 &> /dev/null; then
        echo "pip3 not found. Installing pip3..."
        sudo apt update
        sudo apt install -y python3-pip
    else
        echo "pip3 is already installed."
    fi
}

# Function to check if Microsoft Edge is installed, and install if not
install_edge_if_needed() {
    if ! command -v microsoft-edge &> /dev/null; then
        echo "Microsoft Edge not found. Installing Microsoft Edge..."
        sudo apt update
        sudo apt install -y wget
        wget https://packages.microsoft.com/repos/edge/pool/main/m/microsoft-edge-stable/microsoft-edge-stable_109.0.1518.78-1_amd64.deb
        sudo dpkg -i microsoft-edge-stable_109.0.1518.78-1_amd64.deb
        sudo apt --fix-broken install -y
        echo "Microsoft Edge installed."
    else
        echo "Microsoft Edge is already installed."
    fi
}

# Function to create and activate a virtual environment
create_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv $VENV_DIR
    fi
    echo "Activating virtual environment..."
    source $VENV_DIR/bin/activate
}

# Function to install dependencies from requirements.txt
install_requirements() {
    if [ -f "requirements.txt" ]; then
        echo "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        echo "requirements.txt not found, skipping dependency installation."
    fi
}

# Start the bot function
start_bot() {
    echo "Starting the bot..."
    nohup python3 $BOT_SCRIPT > $LOG_FILE 2>&1 &
    BOT_PID=$!
    echo "Bot started with PID $BOT_PID"
}

# Stop the bot function
stop_bot() {
    if [ -n "$BOT_PID" ]; then
        echo "Stopping the bot with PID $BOT_PID"
        kill $BOT_PID
        wait $BOT_PID 2>/dev/null
        echo "Bot stopped."
    fi
}

# Install pip3 if not installed
install_pip

# Install Microsoft Edge if not installed
install_edge_if_needed

# Create and activate virtual environment
create_venv

# Install dependencies from requirements.txt
install_requirements

# Start the bot immediately
start_bot

# Run monitoring loop to check for updates
while true; do
    echo "Checking for updates..."

    # Fetch updates from the remote repository
    git fetch origin $BRANCH > fetch_output.log 2>&1

    if [ $? -ne 0 ]; then
        echo "Git fetch failed! Check fetch_output.log for details."
        sleep 60
        continue
    fi

    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/$BRANCH)

    echo "LOCAL Commit Hash: $LOCAL"
    echo "REMOTE Commit Hash: $REMOTE"

    # Force pull the latest updates from the remote main-dev branch
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "Changes detected. Force pulling updates from $BRANCH..."
        git reset --hard origin/$BRANCH > pull_output.log 2>&1  # Force pull and reset to the remote main-dev branch

        if [ $? -ne 0 ]; then
            echo "Git pull failed! Check pull_output.log for details."
            sleep 60
            continue
        fi

        echo "Updating dependencies after pull..."
        install_requirements

        echo "Restarting the bot..."

        # Stop the current bot and start it again
        stop_bot
        start_bot
    fi

    # Wait before checking for updates again
    sleep 60
done