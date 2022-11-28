#!/bin/bash

# Set dev-venv path variable
source ./scripts/set_dev_venv_variable.sh

# Remove existing dev-venv folder to have a clean install
echo " -- Remove existing $DEV_VENV_PATH"
rm -rf $DEV_VENV_PATH

# Create virtual environment
echo " -- Create virtual environment $DEV_VENV_PATH"
python3.10 -m venv $DEV_VENV_PATH

# Activate virtual environmnet
echo " -- Activate virtual environment $DEV_VENV_PATH"
source $DEV_VENV_PATH/bin/activate

# Upgrade pip
echo " -- Upgrade pip"
python3.10 -m pip install --upgrade pip

# Install packages
# Use this on first run of script
# pip install pylama[mypy,vulture,pylint] pre-commit bandit
echo " -- Install packages from requirements file"
pip install -r requirements/dev-venv.txt