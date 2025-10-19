#!/bin/bash

# Script to set up the Python environment for "emotionally-intelligent-chatbots-benchmark"

# Step 1: Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
  echo "Error: requirements.txt not found in the current directory."
  exit 1
fi

# Step 2: Check if src directory exists
if [ ! -d "src" ]; then
  echo "Error: src directory not found in the current directory."
  exit 1
fi

# Step 3: Navigate to the src directory
cd src

# Step 4: Create a virtual environment inside the 'src' directory
python3.12 -m venv _emotionally-intelligent-chatbots-benchmark

# Step 5: Activate the virtual environment
source _emotionally-intelligent-chatbots-benchmark/bin/activate

# Step 6: Upgrade pip to the latest version
python3.12 -m pip install --upgrade setuptools wheel cython pip

# Step 7: Install dependencies from requirements.txt
python3.12 -m pip install -r ../requirements.txt

# Step 8: Install en_core_web_sm (English language model for spaCy)
python3.12 -m spacy download en_core_web_sm

# Step 9: Install Playwright
playwright install