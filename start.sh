#!/bin/bash
#for a timed test do the following
#runs quick battle as civilian faction and exits after N seconds:
#bash start.sh --ai-test civilian 10

cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install -r code/requirements.txt
cd code && python3 twe.py "$@"
