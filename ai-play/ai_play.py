"""UI for a local vision model playing TWE.

Left pane: the game window. Top right: the game process log.
Bottom right: what the model decided and which tools it called.
"""

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from game_session import GameSession
from player import CLEF_ENDPOINT, Player

HERE = Path(__file__).resolve().parent
TWE_ROOT = HERE.parent

BG = "#241f1b"
PANEL = "#1a1613"
FG = "#efe8dc"
MUTED = "#b3a898"
ACCENT = "#d7a15e"
DANGER = "#e07a62"
CLEF_ON = "#8fbf7f"
# The pygame surface is 1280x720. A smaller dock crops that surface from the
# center, which cuts off the text along the left edge.
GAME_W = 1280
GAME_H = 720


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TWE AI Play")
        self.root.configure(bg=BG)
        # Wide enough that the game pane can hold the full 1280x720 surface.
        self.root.geometry("1860x1040")
        self.root.minsize(1860, 1040)
        self.events = queue.Queue()
        self.session = GameSession(TWE_ROOT, on_log=self._enqueue_log)
        self.player = Player(
            self.session, HERE / "prompt.txt", on_decision=self._enqueue_decision
        )
        self._fit_job = None
        self._build()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.after(100, self._drain)
        self.root.after(400, self._keep_game_in_pane)

    def _build(self):
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(8, 0))

        self.faction = tk.StringVar(value="german")
        self.battle = tk.StringVar(value="1")
        self.endpoint = tk.StringVar(value="http://10.12.0.50:8000/v1")
        self.model = tk.StringVar(value="deepseek-ai/DeepSeek-V4-Flash-Vision-Exp")
        self.clef_endpoint = tk.StringVar(value=CLEF_ENDPOINT)
        self.status = tk.StringVar(value="Launch a quick battle, then start the player.")

        self._label(bar, "Faction")
        faction = ttk.Combobox(
            bar, textvariable=self.faction, width=10, state="readonly",
            values=("german", "soviet", "civilian"),
        )
        faction.pack(side=tk.LEFT, padx=(4, 10))
        self._label(bar, "Battle")
        battle = ttk.Combobox(
            bar, textvariable=self.battle, width=4, state="readonly",
            values=("1", "2", "3", "4"),
        )
        battle.pack(side=tk.LEFT, padx=(4, 10))

        self.launch_button = self._button(bar, "Launch game", self._launch)
        self.play_button = self._button(bar, "Start player", self._start_player)
        self.stop_button = self._button(bar, "Stop player", self._stop_player)
        self.play_button.configure(state=tk.DISABLED)
        # Off by default. DeepSeek takes every turn until this is pressed.
        self.clef_button = tk.Button(
            bar, text="Clef off", command=self._toggle_clef,
            bg=PANEL, fg=FG, activebackground="#3a332c", activeforeground=FG,
            relief=tk.FLAT, padx=10, pady=4,
        )
        self.clef_button.pack(side=tk.LEFT, padx=(0, 8))

        endpoint_row = tk.Frame(self.root, bg=BG)
        endpoint_row.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(6, 0))
        self._label(endpoint_row, "Endpoint")
        tk.Entry(
            endpoint_row, textvariable=self.endpoint, width=42,
            bg=PANEL, fg=FG, insertbackground=FG, relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=(4, 10))
        self._label(endpoint_row, "Model")
        tk.Entry(
            endpoint_row, textvariable=self.model, width=52,
            bg=PANEL, fg=FG, insertbackground=FG, relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=(4, 10))
        self._label(endpoint_row, "Clef")
        tk.Entry(
            endpoint_row, textvariable=self.clef_endpoint, width=36,
            bg=PANEL, fg=FG, insertbackground=FG, relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=(4, 0))
        self.clef_endpoint.trace_add("write", self._clef_endpoint_changed)
        self.player.set_clef_url(self.clef_endpoint.get())

        tk.Label(
            self.root, textvariable=self.status, bg=BG, fg=MUTED, anchor="w",
        ).pack(side=tk.TOP, fill=tk.X, padx=12, pady=(4, 6))

        panes = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL, bg=BG, sashwidth=6, sashrelief=tk.FLAT,
        )
        panes.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.panes = panes

        game_wrap = tk.Frame(panes, bg="#000000")
        tk.Label(
            game_wrap, text="Game", bg="#000000", fg=ACCENT, anchor="w",
            font=("TkDefaultFont", 11, "bold"),
        ).pack(side=tk.TOP, fill=tk.X, padx=8, pady=(6, 2))
        self.game_frame = tk.Frame(game_wrap, bg="#000000", width=GAME_W, height=GAME_H)
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        panes.add(game_wrap, stretch="always", minsize=GAME_W)

        side = tk.PanedWindow(
            panes, orient=tk.VERTICAL, bg=BG, sashwidth=6, sashrelief=tk.FLAT,
        )
        self.log_text = self._pane(side, "Game log", minsize=180)
        self.decision_text = self._pane(side, "Decisions", minsize=180)
        panes.add(side, stretch="always", minsize=380)

        self.game_frame.bind("<Configure>", self._schedule_fit)
        # Moving the toplevel does not resize the pane, but the game has to follow.
        self.root.bind("<Configure>", self._schedule_fit)
        # The pane width is not real until the window is on screen.
        self.root.after(50, self._give_game_room)

    def _give_game_room(self):
        """Keep the sash from leaving the game pane narrower than the surface."""
        total = self.panes.winfo_width()
        if total < GAME_W + 64:
            return
        game_w = max(GAME_W, total - 6 - 460)
        self.panes.sash_place(0, game_w, 1)

    def _label(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=MUTED).pack(side=tk.LEFT)

    def _button(self, parent, text, command):
        button = tk.Button(
            parent, text=text, command=command,
            bg=ACCENT, fg="#1a1613", activebackground="#e6c089",
            relief=tk.FLAT, padx=10, pady=4,
        )
        button.pack(side=tk.LEFT, padx=(0, 8))
        return button

    def _pane(self, parent, title, minsize):
        wrap = tk.Frame(parent, bg=PANEL)
        tk.Label(
            wrap, text=title, bg=PANEL, fg=ACCENT, anchor="w",
            font=("TkDefaultFont", 11, "bold"),
        ).pack(side=tk.TOP, fill=tk.X, padx=8, pady=(6, 2))
        text = tk.Text(
            wrap, bg=PANEL, fg=FG, insertbackground=FG, relief=tk.FLAT,
            wrap=tk.WORD, font=("DejaVu Sans Mono", 10), padx=8, pady=6,
            state=tk.DISABLED,
        )
        scroll = tk.Scrollbar(wrap, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        parent.add(wrap, stretch="always", minsize=minsize)
        return text

    def _launch(self):
        if self.session.running():
            self.status.set("The game is already running.")
            return
        faction = self.faction.get()
        battle = self.battle.get()
        try:
            self.session.start(faction, battle)
        except Exception as exc:
            self.status.set(str(exc))
            return
        self.launch_button.configure(state=tk.DISABLED)
        self.status.set(f"Starting a {faction} quick battle ({battle}). Waiting for the window.")
        self._append(self.log_text, f"[launch] {faction} battle {battle}\n")

        def wait():
            try:
                self.session.wait_for_window()
            except Exception as exc:
                self.events.put(("status", str(exc)))
                self.events.put(("enable-launch", None))
                return
            self.events.put(("attach", None))

        threading.Thread(target=wait, daemon=True).start()

    def _start_player(self):
        if not self.session.running() or not self.session._win:
            self.status.set("Launch the game first.")
            return
        if self.player.running():
            self.status.set("The player is already running.")
            return
        endpoint = self.endpoint.get().strip()
        model = self.model.get().strip()
        self.player.start(endpoint, model)
        self.play_button.configure(state=tk.DISABLED)
        if self.player.clef_enabled():
            self.status.set(f"Player running. {model}. Clef walks the simple frames.")
        else:
            self.status.set(f"Player running. {model}.")

    def _clef_endpoint_changed(self, *_args):
        self.player.set_clef_url(self.clef_endpoint.get())

    def _toggle_clef(self):
        enabled = not self.player.clef_enabled()
        self.player.set_clef(enabled)
        if enabled:
            self.clef_button.configure(
                text="Clef on", bg=CLEF_ON, fg="#1a1613",
                activebackground="#a5d09a", activeforeground="#1a1613",
            )
            self.status.set(
                "Clef on. It walks the simple frames. DeepSeek takes enemies, vehicles, menus, and death screens."
            )
        else:
            self.clef_button.configure(
                text="Clef off", bg=PANEL, fg=FG,
                activebackground="#3a332c", activeforeground=FG,
            )
            self.status.set("Clef off. DeepSeek takes every turn.")

    def _stop_player(self):
        self.player.stop()
        self.play_button.configure(state=tk.NORMAL)
        self.status.set("Player stopped. The game is still running.")

    def _enqueue_log(self, line):
        self.events.put(("log", line))

    def _enqueue_decision(self, decision):
        self.events.put(("decision", decision))

    def _drain(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "log":
                    self._append(self.log_text, payload + "\n")
                    if payload.startswith("[game exited"):
                        self.player.stop()
                        self.launch_button.configure(state=tk.NORMAL)
                        self.play_button.configure(state=tk.DISABLED)
                        self.status.set(payload)
                elif kind == "decision":
                    self._show_decision(payload)
                elif kind == "status":
                    self.status.set(payload)
                elif kind == "attach":
                    self._attach_game()
                elif kind == "enable-launch":
                    self.launch_button.configure(state=tk.NORMAL)
        except queue.Empty:
            pass
        self.root.after(100, self._drain)

    def _attach_game(self):
        try:
            self.session.attach(self.game_frame)
        except Exception as exc:
            self.status.set(f"Could not place the game window: {exc}")
            self.launch_button.configure(state=tk.NORMAL)
            return
        self.play_button.configure(state=tk.NORMAL)
        self.status.set("Game is in the left pane. Start the player when you want it to take over.")

    def _show_decision(self, decision):
        parts = [decision["time"]]
        if decision.get("source"):
            parts.append(decision["source"])
        response_s = _span(decision.get("response_s"))
        since_s = _span(decision.get("since_s"))
        if response_s:
            parts.append(f"{response_s} response")
        if since_s:
            parts.append(f"{since_s} since previous")
        lines = ["--- " + " · ".join(parts) + " ---"]
        if decision.get("text"):
            lines.append(decision["text"])
        for result in decision.get("results") or []:
            lines.append(result)
        if decision.get("error"):
            lines.append("(error)")
        lines.append("")
        self._append(self.decision_text, "\n".join(lines) + "\n")
        if decision.get("error"):
            self.status.set(decision.get("text") or "The player hit an error.")
        elif response_s:
            who = decision.get("source") or "model"
            detail = f"Last {who} response {response_s}."
            if since_s:
                detail = f"Last {who} response {response_s} ({since_s} since the previous)."
            self.status.set(detail)

    def _append(self, widget, text):
        widget.configure(state=tk.NORMAL)
        widget.insert(tk.END, text)
        # Keep the panes bounded. The full log also lives on the session.
        end = int(widget.index("end-1c").split(".")[0])
        if end > 2500:
            widget.delete("1.0", f"{end - 2000}.0")
        widget.see(tk.END)
        widget.configure(state=tk.DISABLED)

    def _schedule_fit(self, _event):
        if self._fit_job is not None:
            self.root.after_cancel(self._fit_job)
        self._fit_job = self.root.after(150, self._fit_now)

    def _fit_now(self):
        self._fit_job = None
        if self.session._win:
            try:
                self.session.fit(self.game_frame)
            except Exception:
                pass

    def _keep_game_in_pane(self):
        # While this window is focused, keep the game glued to the pane.
        # The transient hint holds z-order, including across a click or drag.
        # Skip the raise when another application is in front.
        if self.session.placed and self.session._win and self.root.focus_displayof():
            try:
                self.session.fit(self.game_frame)
            except Exception:
                pass
        self.root.after(200, self._keep_game_in_pane)

    def _close(self):
        self.player.stop()
        self.session.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def _span(seconds):
    if seconds is None:
        return ""
    seconds = float(seconds)
    if seconds < 10:
        return f"{seconds:.1f}s"
    return f"{round(seconds)}s"


if __name__ == "__main__":
    App().run()
