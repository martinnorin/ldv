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
# Either clean install has been requested or requirements file doesn't exist
if [[ ! -f "requirements/dev-venv.txt" ]]
then
    echo " -- Install packages by name"
    # Install packages
    # pip install pylama[mypy,vulture,pylint] pre-commit bandit boto3 requests pyarrow pandas haversine
    pip install build twine
    # Install our package in dev mode
    pip install -e .[ALL]
    # Create requirements file without our package
    pip freeze --exclude-editable > requirements/dev-venv.txt
    # Add our package in dev mode to requirements file
    echo "-e ." >> requirements/dev-venv.txt
else
    # File exists and will be used for installation
    echo " -- Install packages from requirements file"
    pip install -r requirements/dev-venv.txt
fi