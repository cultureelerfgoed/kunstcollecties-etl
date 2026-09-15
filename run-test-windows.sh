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
python src/harvest_service.py --chunks '7000' --testmode 'True'

# generate implementation diagram
cd tools 
python criteria.py 'ontology' '../data/kc-pt-0.jsonld' 'kc.mmd'
..
