"""Ask the local vision model what to do, then run the tool calls on the game."""

import base64
import json
import threading
import time
from datetime import datetime
from pathlib import Path

import requests

_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": (
                "Press a key once. Use this for menus, zoom, reload, prone, "
                "the map, and throwing. Do not use it to walk or shoot."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": (
                            "One of: tab, esc, space, r, p, g, t, m, z, x, "
                            "[, ], -, +, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9"
                        ),
                    },
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hold_key",
            "description": (
                "Hold a key. w/a/s/d walk or drive. f fires at the current mouse "
                "position. up/down/left/right are vehicle throttle and turret keys. "
                "Only one direction works at a time."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "One of: w, a, s, d, f, up, down, left, right",
                    },
                    "seconds": {
                        "type": "number",
                        "description": "How long to hold the key, from 0.15 to 20.",
                    },
                },
                "required": ["key", "seconds"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aim",
            "description": (
                "Move the mouse. x and y are fractions of the game picture, "
                "0 to 1, origin at the top left. The soldier is at the center. "
                "Call this before hold_key f, press_key g, or press_key t."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": (
                "Left-click a point in the game picture to select a nearby "
                "soldier, vehicle, or container and open its menu. "
                "x and y are fractions of the picture, 0 to 1."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wait",
            "description": "Let the simulation run without touching the controls.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "number",
                        "description": "How long to wait, from 0.2 to 10.",
                    },
                },
                "required": ["seconds"],
            },
        },
    },
]

_MAX_CALLS = 6


class Player:
    """One background thread that looks, decides, and acts."""

    def __init__(self, session, prompt_path, on_decision):
        self.session = session
        self.prompt_path = Path(prompt_path)
        self.on_decision = on_decision
        self.stop_event = threading.Event()
        self._thread = None
        self._actions = []
        self._plan = ""
        self._turn = 0
        self._started = None
        self._last_decision_at = None
        self._last_request_s = None
        self._holding = False
        self._overlap_wait = 0.0

    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self, llm_url, model):
        if self.running():
            return
        self.stop_event.clear()
        self._actions = []
        self._plan = ""
        self._turn = 0
        self._started = time.time()
        self._last_decision_at = None
        self._last_request_s = None
        self._holding = False
        self._overlap_wait = 0.0
        self._thread = threading.Thread(
            target=self._loop, args=(llm_url.rstrip("/"), model), daemon=True
        )
        self._thread.start()

    def stop(self):
        self.stop_event.set()
        try:
            self.session.release_hold()
        except Exception:
            pass
        self._holding = False

    def _loop(self, llm_url, model):
        system = self.prompt_path.read_text(encoding="utf-8")
        self._started = time.time()
        while not self.stop_event.is_set():
            started = time.time()
            try:
                self._step(llm_url, model, system)
            except Exception as exc:
                self.session.release_hold()
                self._holding = False
                self._emit(
                    f"The request failed: {exc}", [], error=True,
                    response_s=self._last_request_s,
                )
                self._sleep(3)
                continue
            # A fast empty reply should not spin the endpoint.
            # A key left down should roll straight into the next picture.
            if not self._holding and time.time() - started < 1.5:
                self._sleep(1.5)

    def _step(self, llm_url, model, system):
        jpeg = self.session.screenshot_jpeg()
        data_url = "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")
        self._turn += 1
        elapsed = _elapsed(time.time() - (self._started or time.time()))
        actions = "\n".join(self._actions[-20:]) or "(none yet)"
        plan = self._plan or "(none yet)"
        text = (
            "This is the current game picture. Act from what you can see.\n\n"
            f"Turn {self._turn}. You have been playing for {elapsed}.\n\n"
            f"Your plan: {plan}\n\n"
            "Recent actions, oldest first:\n"
            f"{actions}\n"
        )
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ]
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 800,
            "tools": _TOOLS,
            "tool_choice": "auto",
        }
        self._last_request_s = None
        request_started = time.time()
        try:
            response = requests.post(
                f"{llm_url}/chat/completions",
                json=payload,
                timeout=180,
            )
        finally:
            self._last_request_s = time.time() - request_started
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:400]}")
        # The picture was taken while the previous hold was still down.
        # Let that key go before this reply's own actions.
        self.session.release_hold()
        self._holding = False
        message = response.json().get("choices", [{}])[0].get("message", {})
        said = (message.get("content") or "").strip()
        calls = message.get("tool_calls") or []
        usable = calls[:_MAX_CALLS]
        overlap = bool(usable) and _call_name(usable[-1]) == "hold_key"
        body = usable[:-1] if overlap else usable
        results = []
        for call in body:
            if self.stop_event.is_set():
                results.append("stopped")
                break
            results.append(self._remember_action(call))
        if overlap and not self.stop_event.is_set():
            results.append(self._begin_overlap(usable[-1]))
        if len(calls) > _MAX_CALLS:
            results.append(f"ignored {len(calls) - _MAX_CALLS} extra tool calls")
        if not said and not results:
            said = "(no decision and no tool calls)"
        sentence = _plan_sentence(said)
        if sentence and sentence != "(no decision and no tool calls)":
            self._plan = sentence
        self._emit(said, results, error=False, response_s=self._last_request_s)
        self._sleep_while_holding()

    def _begin_overlap(self, call):
        """Hold the last key of this reply, and leave it down for the next request."""
        name, args, error = _parse_call(call)
        if error:
            return f"{name}: error: {error}"
        key = str(args.get("key", ""))
        seconds = _hold_seconds(args.get("seconds", 1))
        out = self.session.hold_down(key)
        result = f"{name}({_brief(args)}) -> {out}"
        if "error" in out.lower():
            self._actions.append(f"turn {self._turn}: {_compact_action(name, args, result)}")
            del self._actions[:-20]
            return result
        lead = self._last_request_s if self._last_request_s else 4.0
        lead = max(0.8, min(lead + 0.5, 20.0))
        self._overlap_wait = max(0.0, seconds - lead)
        self._holding = True
        self._actions.append(f"turn {self._turn}: {_compact_action(name, args, out)}")
        del self._actions[:-20]
        return (
            f"{name}({_brief(args)}) -> holding {key} for {seconds:.1f}s "
            "during the next response"
        )

    def _sleep_while_holding(self):
        if not self._holding:
            return
        end = time.time() + self._overlap_wait
        while time.time() < end:
            if self.stop_event.is_set():
                self.session.release_hold()
                self._holding = False
                return
            time.sleep(0.05)

    def _run_tool(self, call):
        function = call.get("function", {})
        name = function.get("name", "")
        raw = function.get("arguments", "{}")
        if isinstance(raw, str):
            try:
                args = json.loads(raw or "{}")
            except json.JSONDecodeError:
                return f"{name}: error: arguments were not valid json"
        elif isinstance(raw, dict):
            args = raw
        else:
            args = {}
        try:
            if name == "press_key":
                out = self.session.press(str(args.get("key", "")))
            elif name == "hold_key":
                out = self.session.hold(
                    str(args.get("key", "")), args.get("seconds", 1), self.stop_event
                )
            elif name == "aim":
                out = self.session.aim(args.get("x"), args.get("y"))
            elif name == "click":
                out = self.session.click(args.get("x"), args.get("y"))
            elif name == "wait":
                out = self.session.wait(args.get("seconds", 1), self.stop_event)
            else:
                out = f"error: unknown tool {name}"
        except Exception as exc:
            out = f"error: {exc}"
        return f"{name}({_brief(args)}) -> {out}"

    def _remember_action(self, call):
        result = self._run_tool(call)
        function = call.get("function", {})
        name = function.get("name", "")
        raw = function.get("arguments", "{}")
        if isinstance(raw, str):
            try:
                args = json.loads(raw or "{}")
            except json.JSONDecodeError:
                args = {}
        elif isinstance(raw, dict):
            args = raw
        else:
            args = {}
        self._actions.append(f"turn {self._turn}: {_compact_action(name, args, result)}")
        del self._actions[:-20]
        return result

    def _emit(self, text, results, error, response_s=None):
        now = time.time()
        since_s = None
        if self._last_decision_at is not None:
            since_s = now - self._last_decision_at
        self._last_decision_at = now
        if self.on_decision:
            self.on_decision({
                "time": datetime.now().strftime("%H:%M:%S"),
                "text": text,
                "results": results,
                "error": error,
                "response_s": response_s,
                "since_s": since_s,
            })

    def _sleep(self, seconds):
        end = time.time() + seconds
        while time.time() < end and not self.stop_event.is_set():
            time.sleep(0.05)


def _call_name(call):
    return call.get("function", {}).get("name", "")


def _parse_call(call):
    function = call.get("function", {})
    name = function.get("name", "")
    raw = function.get("arguments", "{}")
    if isinstance(raw, str):
        try:
            args = json.loads(raw or "{}")
        except json.JSONDecodeError:
            return name, {}, "arguments were not valid json"
    elif isinstance(raw, dict):
        args = raw
    else:
        args = {}
    return name, args, ""


def _hold_seconds(value):
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        seconds = 1.0
    return max(0.15, min(seconds, 20.0))


def _brief(args):
    parts = []
    for key, value in args.items():
        if isinstance(value, float):
            parts.append(f"{key}={value:.2f}")
        else:
            parts.append(f"{key}={value}")
    return ", ".join(parts)


def _elapsed(seconds):
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"{seconds}s"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {seconds}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m"


def _seconds(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "?s"
    if abs(number - round(number)) < 0.05:
        return f"{int(round(number))}s"
    return f"{number:.1f}s"


def _compact_action(name, args, out):
    if name == "press_key":
        line = f"press {args.get('key', '?')}"
    elif name == "hold_key":
        line = f"hold {args.get('key', '?')} {_seconds(args.get('seconds', 1))}"
    elif name == "aim":
        line = f"aim {_coord(args.get('x'))},{_coord(args.get('y'))}"
    elif name == "click":
        line = f"click {_coord(args.get('x'))},{_coord(args.get('y'))}"
    elif name == "wait":
        line = f"wait {_seconds(args.get('seconds', 1))}"
    else:
        line = name or "unknown"
    lower = out.lower()
    if "error:" in lower:
        reason = out[lower.index("error:") + len("error:"):].strip()
        if len(reason) > 60:
            reason = reason[:57] + "..."
        line += f" failed ({reason})" if reason else " failed"
    return line


def _coord(value):
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "?"


def _plan_sentence(text):
    """The last sentence is the plan the next turn repeats."""
    words = " ".join(text.split())
    if not words:
        return ""
    parts = []
    buf = []
    for ch in words:
        buf.append(ch)
        if ch in ".!?":
            piece = "".join(buf).strip()
            if piece:
                parts.append(piece)
            buf = []
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts[-1] if parts else ""
