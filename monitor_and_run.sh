#!/usr/bin/env bash
# Keeps the ARES Discord bot running and restarts it when `main` moves.
#
#   chmod +x ./monitor_and_run.sh
#   nohup ./monitor_and_run.sh > monitor.log 2>&1 &
#
# Stop with: pkill -f 'release/bot'
set -euo pipefail

readonly BRANCH="main"
readonly CHECK_INTERVAL=60
readonly LOG_FILE="bot.log"

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# Honours a workspace target directory as well as a standalone checkout.
binary_path() {
    local dir
    dir=$(cargo metadata --no-deps --format-version 1 \
        | sed -n 's/.*"target_directory":"\([^"]*\)".*/\1/p')
    echo "${dir:-target}/release/bot"
}

build() {
    log "Building..."
    cargo build --release --bin bot
    log "Build complete"
}

stop_bot() {
    local pids
    pids=$(pgrep -f "release/bot$" || true)
    [ -z "$pids" ] && return 0

    log "Stopping bot: $pids"
    # shellcheck disable=SC2086
    kill $pids 2>/dev/null || true
    for _ in {1..10}; do
        pgrep -f "release/bot$" >/dev/null || return 0
        sleep 1
    done

    log "Bot did not exit; forcing"
    pkill -9 -f "release/bot$" 2>/dev/null || true
}

start_bot() {
    stop_bot
    local binary
    binary=$(binary_path)
    log "Starting $binary"
    nohup "$binary" >> "$LOG_FILE" 2>&1 &
    log "Bot started with PID $!"
}

# Prints "updated" when the branch moved, nothing when it did not.
check_for_updates() {
    git fetch origin "$BRANCH" --quiet || { log "WARNING: git fetch failed"; return; }

    local local_hash remote_hash
    local_hash=$(git rev-parse HEAD)
    remote_hash=$(git rev-parse "origin/$BRANCH")
    [ "$local_hash" = "$remote_hash" ] && return

    log "Update detected: $local_hash -> $remote_hash"
    git reset --hard "origin/$BRANCH" --quiet || { log "ERROR: reset failed"; return; }
    echo updated
}

trap 'log "Shutting down"; stop_bot; exit 0' INT TERM

log "Initialising bot monitor"
build
start_bot

while true; do
    sleep "$CHECK_INTERVAL"

    if [ -n "$(check_for_updates)" ]; then
        build
        start_bot
    elif ! pgrep -f "release/bot$" >/dev/null; then
        log "Bot is not running; restarting"
        start_bot
    fi
done
