#!/bin/sh

# Harvesting

## Dependencies
echo Setting up Python environment 
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

## Test
echo Running tests.. 
python -m pytest -s tests/ 

# Run 
python src/harvest_service.py --chunks '7000'




