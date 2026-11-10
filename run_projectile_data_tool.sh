#!/bin/bash
# Projectile data review tool. Charts and a table of projectile_data penetration.
# Usage: bash run_projectile_data_tool.sh

cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install -r code/requirements.txt
cd code/tools && python3 projectile_data_tool.py "$@"
