#!/bin/bash
# Squad data review tool. List and a table of squad_data.
# Usage: bash run_squad_data_tool.sh

cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install -r code/requirements.txt
cd code/tools && python3 squad_data_tool.py "$@"
