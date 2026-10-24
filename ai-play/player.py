"""Ask the local vision model what to do, then run the tool calls on the game.

Clef is optional. While it is off, every turn goes to the chat model.
While it is on, Clef walks the simple frames and yields to the chat model
for enemies, vehicles, menus, and death screens.
"""

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
                "Only one direction works at a time. The key stays down until the "
                "next picture, which is taken as soon as you reply. Do not pass a duration."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "One of: w, a, s, d, f, up, down, left, right",
                    },
                },
                "required": ["key"],
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

# Decision model on this machine. It does not generate text.
# The UI shows this and the player posts to {endpoint}/systemone.
CLEF_ENDPOINT = "http://127.0.0.1:8089/v1"
# How often the chat model looks even while Clef is confident.
_CLEF_AUDIT_S = 20.0
_CLEF_MOVE_MIN_P = 0.45
# A direction already held can keep going through a brief dip.
_CLEF_HELD_MIN_P = 0.30
_CLEF_SCENE_MIN_P = 0.35
# A weak "menu" read was handing the walk to DeepSeek. Hard scenes yield lower.
_SITUATION_YIELD_MIN_P = {
    "enemy": 0.40,
    "death": 0.40,
    "vehicle": 0.50,
    "menu": 0.60,
    "unsure": 0.55,
}
_WALK_KEYS = {"w", "a", "s", "d"}
_YIELD_SITUATIONS = {"enemy", "vehicle", "menu", "death", "unsure"}
_WALK_SITUATIONS = {"open", "pin"}
_DIR_NAME = {"w": "north", "a": "west", "s": "south", "d": "east"}

_CLEF_QUESTIONS = {
    "situation": {
        "type": "choice",
        "instructions": (
            "What is in this top-down game picture? The soldier is at the center. "
            "White text on the left is a menu. Green marks near the soldier are map pins."
        ),
        "criteria": {
            "open": "Empty ground. No enemy, no vehicle close by, no menu, no death list.",
            "pin": "A green map pin is visible. No enemy, no vehicle close by, no menu.",
            "enemy": "A hostile soldier or hostile vehicle is visible.",
            "vehicle": "A vehicle is close enough to enter, and no enemy is the main thing on screen.",
            "menu": "A menu is open, shown as white text on the left.",
            "death": "The soldier is dead and a list of other soldiers is on screen.",
            "unsure": "The picture is too unclear to walk safely.",
        },
    },
    "move": {
        "type": "choice",
        "instructions": (
            "Which way should the soldier walk? North is the top of the picture. "
            "Pick yield if a menu, enemy, vehicle, or death screen needs someone else. "
            "If map pins are visible, walk toward them."
        ),
        "criteria": {
            "w": "Walk north, toward the top.",
            "a": "Walk west, toward the left.",
            "s": "Walk south, toward the bottom.",
            "d": "Walk east, toward the right.",
            "wait": "Stand still.",
            "yield": "Do not walk. Someone else should aim, shoot, use a menu, or enter a vehicle.",
        },
    },
}


def clef_act(answers, held_key=""):
    """Turn Clef's answers into walk, wait, or yield.

    The fourth value is how many extra chat-model turns should follow a yield.
    A confident enemy, vehicle, menu, or death screen keeps the chat model for
    a few turns. A weak read gets one look, then Clef takes the clock back.
    """
    situation = _choice_value(answers, "situation")
    move = _choice_value(answers, "move")
    sit_p = _choice_prob(answers, "situation", situation)
    move_p = _choice_prob(answers, "move", move)
    summary = (
        f"Clef sees {situation or 'nothing'} ({sit_p:.0%}), "
        f"move {move or 'none'} ({move_p:.0%})."
    )
    if situation in _YIELD_SITUATIONS:
        need = _SITUATION_YIELD_MIN_P.get(situation, 0.55)
        if sit_p >= need:
            return "yield", f"{situation} ({sit_p:.0%})", summary, 2
        walked = _walk_or_wait(move, move_p, held_key)
        if walked:
            return walked[0], walked[1], summary, 0
        return "yield", f"{situation} ({sit_p:.0%})", summary, 0
    if situation not in _WALK_SITUATIONS:
        return "yield", f"unrecognized situation {situation or 'empty'}", summary, 0
    if move == "yield":
        return "yield", f"yield ({move_p:.0%})", summary, 0
    if sit_p < _CLEF_SCENE_MIN_P:
        return "yield", f"low confidence {situation} ({sit_p:.0%})", summary, 0
    walked = _walk_or_wait(move, move_p, held_key)
    if not walked:
        return "yield", f"low confidence {move or 'empty'} ({move_p:.0%})", summary, 0
    return walked[0], walked[1], summary, 0


def _walk_or_wait(move, move_p, held_key):
    """A confident direction or a wait. None when the move is too weak to act on."""
    if move == "wait":
        if move_p < _CLEF_MOVE_MIN_P:
            return None
        return "wait", ""
    if move not in _WALK_KEYS:
        return None
    floor = _CLEF_HELD_MIN_P if held_key and move == held_key else _CLEF_MOVE_MIN_P
    if move_p < floor:
        return None
    return "walk", move


def _choice_value(answers, qid):
    answer = answers.get(qid) if isinstance(answers, dict) else None
    if not isinstance(answer, dict):
        return ""
    return str(answer.get("choice") or "")


def _choice_prob(answers, qid, key):
    answer = answers.get(qid) if isinstance(answers, dict) else None
    if not isinstance(answer, dict):
        return 0.0
    probs = answer.get("probabilities") or {}
    if not isinstance(probs, dict):
        return 0.0
    try:
        return float(probs.get(key, 0.0))
    except (TypeError, ValueError):
        return 0.0


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
        # Off until the UI turns it on. start() does not clear this.
        self._clef_enabled = False
        self._clef_url = CLEF_ENDPOINT
        self._yield_reason = ""
        self._last_deepseek_at = time.time()
        # After a hard yield, DeepSeek keeps a few turns before Clef looks again.
        self._deepseek_turns_left = 0

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
        self._yield_reason = ""
        self._last_deepseek_at = time.time()
        self._deepseek_turns_left = 0
        self._thread = threading.Thread(
            target=self._loop, args=(llm_url.rstrip("/"), model), daemon=True
        )
        self._thread.start()

    def clef_enabled(self):
        return self._clef_enabled

    def set_clef(self, enabled):
        """Turn the fast model on or off. Safe to call while a turn is in flight."""
        self._clef_enabled = bool(enabled)
        if enabled:
            self._deepseek_turns_left = 0

    def set_clef_url(self, url):
        """Where Clef is served. Safe to change while a turn is in flight."""
        self._clef_url = (url or "").strip() or CLEF_ENDPOINT

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
                # Clef acts on its own frames. A yield falls through to the chat model.
                if not self._clef_enabled or not self._step_clef():
                    self._step(llm_url, model, system)
            except Exception as exc:
                self.session.release_hold()
                self._holding = False
                self._emit(
                    f"The request failed: {exc}", [], error=True,
                    response_s=self._last_request_s, source="deepseek",
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
        reason = self._yield_reason
        self._yield_reason = ""
        if reason:
            text += f"\nThe fast model yielded. Reason: {reason}\n"
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
            # Leaving thinking on spends the whole token budget in the reasoning
            # field and comes back with no text and no tool calls.
            "chat_template_kwargs": {"thinking": False, "enable_thinking": False},
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
        held_through = self.session._held_key if self._holding else ""
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
            # A blank reply must not keep the chat model for the latched turns.
            self._deepseek_turns_left = 0
            if held_through in _WALK_KEYS:
                out = self.session.hold_down(held_through)
                if "error" not in out.lower():
                    self._holding = True
                    self._overlap_wait = 0.0
                    results.append(f"kept holding {held_through}")
        sentence = _plan_sentence(said)
        if sentence and sentence != "(no decision and no tool calls)":
            self._plan = sentence
        self._last_deepseek_at = time.time()
        self._emit(
            said, results, error=False, response_s=self._last_request_s, source="deepseek",
        )
        self._sleep_while_holding()

    def _step_clef(self):
        """Look with Clef. Return True when Clef acted, False to call DeepSeek.

        The key from the previous walk stays down through a yield, so the
        soldier keeps moving while the chat model thinks.
        """
        now = time.time()
        if self._deepseek_turns_left > 0:
            self._deepseek_turns_left -= 1
            self._yield_reason = "DeepSeek still has the scene Clef yielded."
            return False
        if now - self._last_deepseek_at >= _CLEF_AUDIT_S:
            self._yield_reason = "Periodic check while Clef is walking."
            return False
        self._last_request_s = None
        request_started = time.time()
        try:
            jpeg = self.session.screenshot_jpeg()
            answers = _ask_clef(jpeg, self._clef_state(), self._clef_url)
        except Exception as exc:
            self._last_request_s = time.time() - request_started
            self._yield_reason = f"Clef failed: {exc}"
            self._emit(
                f"Clef failed ({exc}). DeepSeek will take this turn.",
                [], error=True, response_s=self._last_request_s, source="clef",
            )
            return False
        self._last_request_s = time.time() - request_started
        held = self.session._held_key if self._holding else ""
        kind, detail, summary, latch = clef_act(answers, held)
        if kind == "yield":
            self._yield_reason = detail
            # latch is the extra turns after this one. A weak read leaves it at 0.
            self._deepseek_turns_left = latch
            self._emit(
                f"{summary} Yielding to DeepSeek: {detail}.",
                [], error=False, response_s=self._last_request_s, source="clef",
            )
            return False
        self._turn += 1
        if kind == "wait":
            self.session.release_hold()
            self._holding = False
            self._plan = "Stand still and look again."
            self._actions.append(f"turn {self._turn}: wait")
            del self._actions[:-20]
            result = "wait -> standing"
        else:
            self._plan = f"Walk {_DIR_NAME.get(detail, detail)} until the scene changes."
            result = self._keep_walking(detail)
        self._emit(
            summary, [result], error=False, response_s=self._last_request_s, source="clef",
        )
        return True

    def _clef_state(self):
        actions = "\n".join(self._actions[-8:]) or "(none yet)"
        plan = self._plan or "(none yet)"
        return (
            "Top-down view of a 1944 battle. The soldier is at the center. "
            "Green marks are map pins. White text on the left is a menu.\n"
            f"Plan: {plan}\n"
            f"Recent actions:\n{actions}"
        )

    def _keep_walking(self, key):
        """Hold a direction and look again on the next loop, without a gap."""
        if self._holding and self.session._held_key == key:
            self._overlap_wait = 0.0
            self._actions.append(f"turn {self._turn}: hold {key}")
            del self._actions[:-20]
            return f"hold_key(key={key}) -> still holding {key}"
        out = self.session.hold_down(key)
        self._actions.append(f"turn {self._turn}: hold {key}")
        del self._actions[:-20]
        if "error" in out.lower():
            self._holding = False
            return f"hold_key(key={key}) -> {out}"
        self._holding = True
        self._overlap_wait = 0.0
        return f"hold_key(key={key}) -> holding {key}"

    def _begin_overlap(self, call):
        """Hold the last key of this reply, and leave it down for the next request."""
        name, args, error = _parse_call(call)
        if error:
            return f"{name}: error: {error}"
        key = str(args.get("key", ""))
        out = self.session.hold_down(key)
        result = f"{name}({_brief(args)}) -> {out}"
        if "error" in out.lower():
            self._actions.append(f"turn {self._turn}: {_compact_action(name, args, result)}")
            del self._actions[:-20]
            return result
        # The next picture is taken immediately. The key stays down through that request.
        self._overlap_wait = 0.0
        self._holding = True
        self._actions.append(f"turn {self._turn}: {_compact_action(name, args, out)}")
        del self._actions[:-20]
        return f"{name}(key={key}) -> holding {key}"

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
                # A hold that is not the last tool of the reply is a tap.
                # The last one stays down and the next picture is taken at once.
                out = self.session.hold(
                    str(args.get("key", "")), 0.15, self.stop_event
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

    def _emit(self, text, results, error, response_s=None, source=""):
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
                "source": source,
            })

    def _sleep(self, seconds):
        end = time.time() + seconds
        while time.time() < end and not self.stop_event.is_set():
            time.sleep(0.05)


def _clef_post_url(endpoint):
    url = (endpoint or "").strip().rstrip("/") or CLEF_ENDPOINT
    if url.endswith("/systemone"):
        return url
    if url.endswith("/v1"):
        return url + "/systemone"
    return url + "/v1/systemone"


def _ask_clef(jpeg, state, endpoint):
    data_url = "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")
    response = requests.post(
        _clef_post_url(endpoint),
        json={"state": state, "images": [data_url], "questions": _CLEF_QUESTIONS},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:400]}")
    answers = response.json().get("answers")
    if not isinstance(answers, dict):
        raise RuntimeError("Clef returned no answers")
    return answers


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
        line = f"hold {args.get('key', '?')}"
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
