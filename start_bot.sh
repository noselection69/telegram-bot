#!/bin/bash
# Start script for Telegram Bot on Linux/Mac

echo "Starting Telegram Finance Bot..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Please create .env file from .env.example with your BOT_TOKEN"
    echo ""
    exit 1
fi

# Start the bot
echo ""
echo "====================================="
echo "Starting bot..."
echo "====================================="
echo ""
python -m bot.main
