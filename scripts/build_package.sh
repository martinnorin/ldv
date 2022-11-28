#!/bin/bash

echo " -- Removing folder and files from previous builds"
rm -rf ./dist
rm -rf ./src/ldv.egg-info

# Upgrade pip
echo " -- Upgrade pip"
pip install --upgrade pip

# Install build package
echo " -- Install and upgrade build package"
pip install --upgrade build

python -m build