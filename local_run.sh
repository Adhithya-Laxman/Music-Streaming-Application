#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Set Flask app environment variable
# export FLASK_APP=main.py
export FLASK_ENV=development

# Run the Flask application
python main.py
# Deactivate the virtual environment when done
deactivate
