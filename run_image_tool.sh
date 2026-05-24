#!/bin/bash
# Sprite alignment / image tool GUI
# Usage: bash start_image_tool.sh

cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install -r code/requirements.txt
cd code/tools && python3 image_tool.py "$@"
