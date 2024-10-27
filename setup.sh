#!/bin/bash

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing packages from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Please make sure to provide it."
    exit 1
fi

echo "Setup complete. The virtual environment is activated."
