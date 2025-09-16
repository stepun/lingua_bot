#!/bin/bash

echo "========================================"
echo "    LinguaBot - AI Translator"
echo "========================================"
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11 or higher"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

echo "Python 3 found: $(python3 --version)"
echo

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3"
    exit 1
fi

echo "Installing requirements..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi

echo
echo "Starting LinguaBot..."
echo "Press Ctrl+C to stop the bot"
echo

# Run the bot
python3 main.py