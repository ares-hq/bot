#!/bin/bash

BOT_SCRIPT="FTCScout.py"
LOG_FILE="ftcscout.log"
VENV_DIR="venv"
BRANCH="main-dev"

install_pip() {
    if ! command -v pip3 &> /dev/null; then
        echo "pip3 not found. Installing pip3..."
        sudo apt update
        sudo apt install -y python3-pip
    else
        echo "pip3 is already installed."
    fi
}

create_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv $VENV_DIR
    fi
    echo "Activating virtual environment..."
    source $VENV_DIR/bin/activate
}

install_requirements() {
    if [ -f "requirements.txt" ]; then
        echo "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        echo "requirements.txt not found, skipping dependency installation."
    fi
}

stop_bot() {
    if pgrep -f "$BOT_SCRIPT" > /dev/null; then
        echo "Stopping the running bot process..."
        pkill -f "$BOT_SCRIPT"
        echo "Bot stopped."
    else
        echo "No bot process is currently running."
    fi
}

start_bot() {
    stop_bot
    echo "Starting the bot..."
    nohup python3 $BOT_SCRIPT > $LOG_FILE 2>&1 &
    echo "Bot started."
}

install_pip

create_venv

install_requirements

start_bot

while true; do
    echo "Checking for updates..."

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

    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "Changes detected. Force pulling updates from $BRANCH..."
        git reset --hard origin/$BRANCH > pull_output.log 2>&1

        if [ $? -ne 0 ]; then
            echo "Git pull failed! Check pull_output.log for details."
            sleep 60
            continue
        fi

        echo "Updating dependencies after pull..."
        install_requirements

        echo "Restarting the bot..."
        start_bot
    fi

    sleep 60
done