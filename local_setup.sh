#!/bin/bash

# Create a virtual environment
python3 -m venv venv
# pip freeze | grep -v 'apturl' > requirements.txt


# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install sqlalchemy
pip install flask-sqlalchemy


source venv/bin/activate


echo "Local setup completed. Activate the virtual environment using 'source venv/bin/activate'."
