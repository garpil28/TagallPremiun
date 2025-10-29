#!/bin/bash
BOT_NAME="tagallbot"
VENV_PATH="$HOME/TagallPremiun/venv"
BOT_PATH="$HOME/TagallPremiun/main.py"

restart_bot() {
    SCREENS=$(screen -ls | grep "$BOT_NAME" | awk -F. '{print $1}' | tr -d '[:space:]')
    if [ -n "$SCREENS" ]; then
        for PID in $SCREENS; do
            screen -S "$PID.$BOT_NAME" -X quit 2>/dev/null
            kill -9 $PID 2>/dev/null
        done
    fi
    source "$VENV_PATH/bin/activate"
    screen -dmS "$BOT_NAME" bash -c "source $VENV_PATH/bin/activate && python3 $BOT_PATH"
}

while true; do
    restart_bot
    sleep 86400
done
