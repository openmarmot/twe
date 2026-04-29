#!/bin/bash
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install -r code/requirements.txt
cd code && python3 twe.py "$@"