#!/bin/bash
# Launch the TWE AI player UI.
# The game itself uses ../venv. This venv is only for the player UI.

cd "$(dirname "$0")"
if [ ! -x venv/bin/python ]; then
  python3 -m venv venv
  ./venv/bin/pip install -r requirements.txt
fi
exec ./venv/bin/python ai_play.py "$@"
