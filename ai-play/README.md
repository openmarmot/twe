# TWE AI Play

A local vision model plays To Whatever End. Designed and tested on a Nvidia DGX Spark.  
One window has three panes:

- **Game** — the pygame window, placed in the left pane
- **Game log** — stdout from the game (who you are, death reports)
- **Decisions** — what the model says it sees, the tools it calls, how long the reply took, and the gap since the previous reply

The model is the OpenAI-compatible server at `http://10.12.0.50:8000/v1`, model `deepseek-ai/DeepSeek-V4-Flash-Vision-Exp`. It gets a screenshot each turn, plus the turn number, how long it has been playing, its last plan sentence, and the last 20 actions. It does not receive the game log. The last key hold of a turn stays down while the next reply is loading, so the soldier keeps moving during that wait. It acts with tools: `press_key`, `hold_key`, `aim`, `click`, and `wait`.

## Run

```bash
cd ai-play
./start.sh
```

Needs `python3-tk` and an X11 session. The game uses the virtualenv in the repo root (`../venv`). Launch a quick battle, then start the player. The player asks the game for a 1280x720 surface and keeps the docked window 16:9 inside the left pane, so it does not cover the log. Clicking or moving AI Play keeps the game on top of that window and follows the pane. A normal launch of TWE is unchanged and still picks its own desktop size.

Battle sizes match the in-game menu: 1 is the smaller random battle, 4 is the test layout.

Edit `prompt.txt` to change how it plays. The endpoint and model can be changed in the window before the player starts.
