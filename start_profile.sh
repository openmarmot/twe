#!/bin/bash
# Profiles the game and opens snakeviz
# Usage: bash start_profile.sh --ai-test civilian 5

cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install -r code/requirements.txt snakeviz
cd code && python3 -m cProfile -o ../profile.prof twe.py "$@"
snakeviz ../profile.prof
