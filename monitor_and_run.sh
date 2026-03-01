#!/bin/bash
set -euo pipefail

# Configuration
readonly BOT_SCRIPT="ARES.py"
readonly LOG_FILE="ARES.log"
readonly VENV_DIR=".venv"
readonly BRANCH="main"
readonly CHECK_INTERVAL=60
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

install_uv() {
    if ! command -v uv &> /dev/null; then
        log "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
}

setup_environment() {
    if [ ! -d "$VENV_DIR" ]; then
        log "Creating virtual environment..."
        uv venv "$VENV_DIR"
    fi
    
    log "Installing dependencies..."
    if [ -f "pyproject.toml" ]; then
        uv sync
    elif [ -f "requirements.txt" ]; then
        uv pip install -r requirements.txt
    fi
}

stop_bot() {
    local pids
    pids=$(pgrep -f "python.*$BOT_SCRIPT" || true)
    
    if [ -n "$pids" ]; then
        log "Stopping bot processes: $pids"
        kill $pids 2>/dev/null || true
        sleep 2
        
        # Force kill if still running
        pids=$(pgrep -f "python.*$BOT_SCRIPT" || true)
        if [ -n "$pids" ]; then
            kill -9 $pids 2>/dev/null || true
        fi
    fi
}

start_bot() {
    stop_bot
    log "Starting bot..."
    nohup "$VENV_DIR/bin/python" "$BOT_SCRIPT" > "$LOG_FILE" 2>&1 &
    log "Bot started with PID $!"
}

check_for_updates() {
    if ! git fetch origin "$BRANCH" 2>&1 | grep -q "fatal"; then
        local local_hash remote_hash
        local_hash=$(git rev-parse HEAD)
        remote_hash=$(git rev-parse "origin/$BRANCH")
        
        if [ "$local_hash" != "$remote_hash" ]; then
            log "Update detected: $local_hash -> $remote_hash"
            git reset --hard "origin/$BRANCH" || {
                log "ERROR: Failed to update repository"
                return 1
            }
            return 0
        fi
    else
        log "WARNING: Git fetch failed"
        return 1
    fi
    return 2
}

# Initialize
log "Initializing bot monitor..."
install_uv
setup_environment
start_bot

# Main loop
while true; do
    sleep "$CHECK_INTERVAL"
    
    if check_for_updates; then
        log "Updating dependencies..."
        setup_environment
        start_bot
    fi
done
