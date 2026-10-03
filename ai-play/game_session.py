"""Run TWE and send it real keyboard and mouse input.

SDL ignores synthetic XSendEvent keypresses, so keys go through the XTest
extension, which is what the game already treats as a physical keyboard.
The pygame window is moved into a frame in the player UI.
"""

import ctypes
import os
import subprocess
import threading
import time
from pathlib import Path

from PIL import Image

# X11
X11 = ctypes.cdll.LoadLibrary("libX11.so.6")
Xtst = ctypes.cdll.LoadLibrary("libXtst.so.6")
X11.XInitThreads.restype = ctypes.c_int
X11.XInitThreads()

X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XOpenDisplay.argtypes = [ctypes.c_char_p]
X11.XDefaultRootWindow.restype = ctypes.c_ulong
X11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
X11.XFlush.argtypes = [ctypes.c_void_p]
X11.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
X11.XFree.argtypes = [ctypes.c_void_p]
X11.XRaiseWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
X11.XMapWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
X11.XSetTransientForHint.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong]
X11.XSetTransientForHint.restype = ctypes.c_int
X11.XMoveResizeWindow.argtypes = [
    ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint
]
X11.XSetInputFocus.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
X11.XKeysymToKeycode.restype = ctypes.c_ubyte
X11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
X11.XInternAtom.restype = ctypes.c_ulong
X11.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
X11.XChangeProperty.argtypes = [
    ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong,
    ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int,
]
X11.XGetWindowAttributes.restype = ctypes.c_int
X11.XQueryTree.restype = ctypes.c_int
X11.XTranslateCoordinates.restype = ctypes.c_int
X11.XFetchName.restype = ctypes.c_int
X11.XFetchName.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_char_p)]
X11.XGetImage.restype = ctypes.c_void_p
X11.XGetImage.argtypes = [
    ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int,
    ctypes.c_uint, ctypes.c_uint, ctypes.c_ulong, ctypes.c_int,
]
X11.XDestroyImage.argtypes = [ctypes.c_void_p]
X11.XDestroyImage.restype = ctypes.c_int

Xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
Xtst.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
Xtst.XTestFakeMotionEvent.argtypes = [
    ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong
]


class _XWindowAttributes(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
        ("border_width", ctypes.c_int),
        ("depth", ctypes.c_int),
        ("visual", ctypes.c_void_p),
        ("root", ctypes.c_ulong),
        ("klass", ctypes.c_int),
        ("bit_gravity", ctypes.c_int),
        ("win_gravity", ctypes.c_int),
        ("backing_store", ctypes.c_int),
        ("backing_planes", ctypes.c_ulong),
        ("backing_pixel", ctypes.c_ulong),
        ("save_under", ctypes.c_int),
        ("colormap", ctypes.c_ulong),
        ("map_installed", ctypes.c_int),
        ("map_state", ctypes.c_int),
        ("all_event_masks", ctypes.c_long),
        ("your_event_mask", ctypes.c_long),
        ("do_not_propagate_mask", ctypes.c_long),
        ("override_redirect", ctypes.c_int),
        ("screen", ctypes.c_void_p),
    ]


class _XImage(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
        ("xoffset", ctypes.c_int),
        ("format", ctypes.c_int),
        ("data", ctypes.c_void_p),
        ("byte_order", ctypes.c_int),
        ("bitmap_unit", ctypes.c_int),
        ("bitmap_bit_order", ctypes.c_int),
        ("bitmap_pad", ctypes.c_int),
        ("depth", ctypes.c_int),
        ("bytes_per_line", ctypes.c_int),
        ("bits_per_pixel", ctypes.c_int),
        ("red_mask", ctypes.c_ulong),
        ("green_mask", ctypes.c_ulong),
        ("blue_mask", ctypes.c_ulong),
    ]


class _MwmHints(ctypes.Structure):
    _fields_ = [
        ("flags", ctypes.c_ulong),
        ("functions", ctypes.c_ulong),
        ("decorations", ctypes.c_ulong),
        ("input_mode", ctypes.c_long),
        ("status", ctypes.c_ulong),
    ]


X11.XGetWindowAttributes.argtypes = [
    ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(_XWindowAttributes)
]
X11.XQueryTree.argtypes = [
    ctypes.c_void_p, ctypes.c_ulong,
    ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong),
    ctypes.POINTER(ctypes.POINTER(ctypes.c_ulong)), ctypes.POINTER(ctypes.c_uint),
]
X11.XTranslateCoordinates.argtypes = [
    ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong,
    ctypes.c_int, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_ulong),
]

# One-shot menu and view keys. Movement and fire use hold_key.
PRESS_KEYS = {
    "tab": 0xFF09,
    "esc": 0xFF1B,
    "space": 0x20,
    "r": 0x72,
    "p": 0x70,
    "g": 0x67,
    "t": 0x74,
    "m": 0x6D,
    "z": 0x7A,
    "x": 0x78,
    "[": 0x5B,
    "]": 0x5D,
    "-": 0x2D,
    "+": 0x3D,
    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
}
HOLD_KEYS = {
    "w": 0x77,
    "a": 0x61,
    "s": 0x73,
    "d": 0x64,
    "f": 0x66,
    "up": 0xFF52,
    "down": 0xFF54,
    "left": 0xFF51,
    "right": 0xFF53,
}

_TITLE = b"openmarmot/twe"
# Human play stays on the game's auto size (up to 1920x1080). The player
# uses a smaller 16:9 surface so the pane and the vision screenshot stay sharp.
SCREEN_SIZE = "1280x720"
_ZPIXMAP = 2


def _walk(display, win, found):
    name = ctypes.c_char_p()
    if X11.XFetchName(display, win, ctypes.byref(name)):
        if name.value and _TITLE in name.value:
            found.append(win)
        X11.XFree(name)
    root = ctypes.c_ulong()
    parent = ctypes.c_ulong()
    children = ctypes.POINTER(ctypes.c_ulong)()
    count = ctypes.c_uint()
    if not X11.XQueryTree(
        display, win, ctypes.byref(root), ctypes.byref(parent),
        ctypes.byref(children), ctypes.byref(count),
    ):
        return
    for i in range(count.value):
        _walk(display, children[i], found)
    if children:
        X11.XFree(children)


def _inner_window(display, win):
    """Use the SDL client when the named window is a window-manager frame.

    The frame draws the title bar. Keys and screenshots belong on the child
    that actually runs the game.
    """
    current = win
    for _ in range(4):
        _rx, _ry, width, height = _geometry(display, current)
        root = ctypes.c_ulong()
        parent = ctypes.c_ulong()
        children = ctypes.POINTER(ctypes.c_ulong)()
        count = ctypes.c_uint()
        if not X11.XQueryTree(
            display, current, ctypes.byref(root), ctypes.byref(parent),
            ctypes.byref(children), ctypes.byref(count),
        ):
            break
        child_ids = [children[i] for i in range(count.value)]
        if children:
            X11.XFree(children)
        best = None
        best_area = 0
        for child in child_ids:
            try:
                _cx, _cy, cw, ch = _geometry(display, child)
            except RuntimeError:
                continue
            area = cw * ch
            if cw > 200 and ch > 200 and area > best_area:
                best = child
                best_area = area
        if best is None or best_area < width * height * 0.45:
            break
        current = best
    return current


def _managed_frame(display, win):
    """The window the WM stacks. Mutter wraps clients in its own frame.

    A transient hint has to name that frame. Naming the Tk client leaves
    the game behind the frame as soon as the frame is clicked or moved.
    """
    root = X11.XDefaultRootWindow(display)
    current = win
    while current not in (0, root):
        root_ret = ctypes.c_ulong()
        parent = ctypes.c_ulong()
        children = ctypes.POINTER(ctypes.c_ulong)()
        count = ctypes.c_uint()
        if not X11.XQueryTree(
            display, current, ctypes.byref(root_ret), ctypes.byref(parent),
            ctypes.byref(children), ctypes.byref(count),
        ):
            break
        if children:
            X11.XFree(children)
        if parent.value in (0, root):
            return current
        current = parent.value
    return win


def _geometry(display, win):
    attr = _XWindowAttributes()
    if not X11.XGetWindowAttributes(display, win, ctypes.byref(attr)):
        raise RuntimeError("XGetWindowAttributes failed")
    rx = ctypes.c_int()
    ry = ctypes.c_int()
    child = ctypes.c_ulong()
    root = X11.XDefaultRootWindow(display)
    X11.XTranslateCoordinates(
        display, win, root, 0, 0, ctypes.byref(rx), ctypes.byref(ry), ctypes.byref(child)
    )
    return rx.value, ry.value, attr.width, attr.height


def _image_from_window(display, win):
    _rx, _ry, width, height = _geometry(display, win)
    if width < 2 or height < 2:
        raise RuntimeError("game window has no size yet")
    raw = X11.XGetImage(
        display, win, 0, 0, width, height, ctypes.c_ulong(0xFFFFFFFFFFFFFFFF), _ZPIXMAP
    )
    if not raw:
        raise RuntimeError("XGetImage failed")
    try:
        xi = ctypes.cast(raw, ctypes.POINTER(_XImage)).contents
        buf = ctypes.string_at(xi.data, xi.bytes_per_line * xi.height)
        if xi.bits_per_pixel != 32:
            raise RuntimeError(f"unsupported screenshot depth {xi.bits_per_pixel}")
        # Little-endian servers store blue in the low byte when blue_mask is 0xff.
        pixel_format = "BGRX" if xi.blue_mask == 0xFF else "RGBX"
        image = Image.frombytes(
            "RGB", (xi.width, xi.height), buf, "raw", pixel_format, xi.bytes_per_line, 1
        )
        return image
    finally:
        X11.XDestroyImage(raw)


class GameSession:
    """One TWE process and the X11 window it creates."""

    def __init__(self, twe_root, on_log):
        self.twe_root = Path(twe_root)
        self.on_log = on_log
        self.proc = None
        self.placed = False
        self._lines = []
        self._log_lock = threading.Lock()
        self._xlock = threading.Lock()
        self._display = X11.XOpenDisplay(None)
        if not self._display:
            raise RuntimeError("could not open the X display")
        self._win = None
        self._fitted = None
        self._held_code = None
        self._held_key = None

    def start(self, faction, battle):
        if self.proc and self.proc.poll() is None:
            raise RuntimeError("the game is already running")
        python = self.twe_root / "venv" / "bin" / "python"
        if not python.is_file():
            python = Path(os.environ.get("TWE_PYTHON", "python3"))
        cmd = [
            str(python), "-u", "twe.py",
            "--screen-size", SCREEN_SIZE,
            "--quick-battle", faction, str(battle),
        ]
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["SDL_VIDEO_WINDOW_POS"] = "60,60"
        self._win = None
        self.placed = False
        self._fitted = None
        with self._log_lock:
            self._lines = []
        self.proc = subprocess.Popen(
            cmd,
            cwd=str(self.twe_root / "code"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            text=True,
            bufsize=1,
        )
        threading.Thread(target=self._read_output, daemon=True).start()

    def _read_output(self):
        proc = self.proc
        if proc is None or proc.stdout is None:
            return
        for line in proc.stdout:
            text = line.rstrip("\n")
            with self._log_lock:
                self._lines.append(text)
                if len(self._lines) > 5000:
                    del self._lines[:1000]
            if self.on_log:
                self.on_log(text)
        code = proc.wait()
        if self.on_log:
            self.on_log(f"[game exited with code {code}]")

    def wait_for_window(self, timeout=90):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.proc and self.proc.poll() is not None:
                raise RuntimeError("the game exited before its window appeared")
            found = []
            with self._xlock:
                root = X11.XDefaultRootWindow(self._display)
                _walk(self._display, root, found)
            if found:
                self._win = _inner_window(self._display, found[-1])
                return self._win
            time.sleep(0.3)
        raise RuntimeError("timed out waiting for the TWE window")

    def attach(self, frame):
        """Put the game window on top of a Tk frame, sized to that frame.

        Reparenting the SDL window into the frame drops keyboard events on
        this desktop, so the window stays a real toplevel and is moved over
        the pane instead.
        """
        if not self._win:
            raise RuntimeError("no game window")
        self.placed = True
        self.fit(frame)
        return "docked"

    def fit(self, frame):
        """Match the game window to the frame after a resize or a restack.

        The surface is 16:9. A taller or wider window letterboxes, and the
        soldier is then no longer at the center of the screenshot. Use the
        largest 16:9 rectangle that fits in the pane.
        """
        if not self._win:
            return
        frame.update_idletasks()
        frame_w = frame.winfo_width()
        frame_h = frame.winfo_height()
        if frame_w < 64 or frame_h < 64:
            return
        width = frame_w
        height = width * 9 // 16
        if height > frame_h:
            height = frame_h
            width = height * 16 // 9
        if width > frame_w or height > frame_h or width < 64 or height < 64:
            return
        x = frame.winfo_rootx() + (frame_w - width) // 2
        y = frame.winfo_rooty() + (frame_h - height) // 2
        owner = int(frame.winfo_toplevel().winfo_id())
        with self._xlock:
            self._strip_decorations()
            # Keep the game above AI Play only. The WM raises the frame on
            # click and drag; the game has to be transient for that frame.
            if owner and owner != self._win:
                managed = _managed_frame(self._display, owner)
                if managed and managed != self._win:
                    X11.XSetTransientForHint(self._display, self._win, managed)
            if self._fitted != (x, y, width, height):
                X11.XMoveResizeWindow(self._display, self._win, x, y, width, height)
                X11.XRaiseWindow(self._display, self._win)
                X11.XMapWindow(self._display, self._win)
                self._fitted = (x, y, width, height)
            X11.XFlush(self._display)

    def _strip_decorations(self):
        # MWM_HINTS_DECORATIONS with an empty decoration mask.
        hints = _MwmHints(1 << 1, 0, 0, 0, 0)
        atom = X11.XInternAtom(self._display, b"_MOTIF_WM_HINTS", 0)
        X11.XChangeProperty(
            self._display, self._win, atom, atom, 32, 0,
            ctypes.cast(ctypes.byref(hints), ctypes.c_void_p), 5,
        )

    def screenshot_jpeg(self, max_edge=1280):
        if not self._win:
            raise RuntimeError("no game window")
        with self._xlock:
            image = _image_from_window(self._display, self._win)
        image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
        import io
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=80, optimize=True)
        return buf.getvalue()

    def recent_log(self, limit=30):
        with self._log_lock:
            lines = self._lines[-limit:]
        return "\n".join(lines)

    def identity_line(self):
        with self._log_lock:
            lines = list(self._lines)
        for line in reversed(lines):
            if line.startswith("You are now "):
                return line
        return ""

    def press(self, key):
        symbol = PRESS_KEYS.get(key)
        if symbol is None:
            known = ", ".join(PRESS_KEYS)
            return f"error: {key!r} is not a one-shot key. Use one of: {known}. Movement and fire use hold_key."
        self._tap(symbol)
        return f"pressed {key}"

    def hold(self, key, seconds, cancel=None):
        symbol = HOLD_KEYS.get(key)
        if symbol is None:
            known = ", ".join(HOLD_KEYS)
            return f"error: {key!r} cannot be held. Use one of: {known}."
        seconds = max(0.15, min(float(seconds), 20.0))
        self.release_hold()
        code = self._keycode(symbol)
        self._focus()
        with self._xlock:
            Xtst.XTestFakeKeyEvent(self._display, code, 1, 0)
            X11.XFlush(self._display)
        end = time.time() + seconds
        try:
            while time.time() < end:
                if cancel is not None and cancel.is_set():
                    return f"held {key} until stopped"
                time.sleep(0.05)
        finally:
            with self._xlock:
                Xtst.XTestFakeKeyEvent(self._display, code, 0, 0)
                X11.XFlush(self._display)
        return f"held {key} for {seconds:.1f}s"

    def hold_down(self, key):
        """Press a hold-key and leave it down until release_hold."""
        symbol = HOLD_KEYS.get(str(key))
        if symbol is None:
            known = ", ".join(HOLD_KEYS)
            return f"error: {key!r} cannot be held. Use one of: {known}."
        self.release_hold()
        code = self._keycode(symbol)
        self._focus()
        with self._xlock:
            Xtst.XTestFakeKeyEvent(self._display, code, 1, 0)
            X11.XFlush(self._display)
        self._held_code = code
        self._held_key = str(key)
        return f"holding {key}"

    def release_hold(self):
        """Release the key left down by hold_down. Safe to call twice."""
        code = self._held_code
        self._held_code = None
        self._held_key = None
        if not code or not self._display:
            return
        with self._xlock:
            Xtst.XTestFakeKeyEvent(self._display, code, 0, 0)
            X11.XFlush(self._display)

    def aim(self, x_frac, y_frac):
        x_frac = _fraction(x_frac)
        y_frac = _fraction(y_frac)
        self._warp(x_frac, y_frac)
        return f"aimed at {x_frac:.2f}, {y_frac:.2f}"

    def click(self, x_frac, y_frac):
        x_frac = _fraction(x_frac)
        y_frac = _fraction(y_frac)
        self._warp(x_frac, y_frac)
        self._focus()
        with self._xlock:
            Xtst.XTestFakeButtonEvent(self._display, 1, 1, 0)
            X11.XFlush(self._display)
            time.sleep(0.04)
            Xtst.XTestFakeButtonEvent(self._display, 1, 0, 0)
            X11.XFlush(self._display)
        return f"clicked {x_frac:.2f}, {y_frac:.2f}"

    def wait(self, seconds, cancel=None):
        seconds = max(0.2, min(float(seconds), 10.0))
        end = time.time() + seconds
        while time.time() < end:
            if cancel is not None and cancel.is_set():
                return "wait cancelled"
            time.sleep(0.05)
        return f"waited {seconds:.1f}s"

    def running(self):
        return self.proc is not None and self.proc.poll() is None

    def close(self):
        self._release_keys()
        proc = self.proc
        self.proc = None
        if proc is None or proc.poll() is not None:
            return
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

    def _release_keys(self):
        self._held_code = None
        self._held_key = None
        if not self._display:
            return
        with self._xlock:
            for symbol in list(HOLD_KEYS.values()) + list(PRESS_KEYS.values()):
                code = X11.XKeysymToKeycode(self._display, symbol)
                if code:
                    Xtst.XTestFakeKeyEvent(self._display, code, 0, 0)
            X11.XFlush(self._display)

    def _tap(self, symbol):
        code = self._keycode(symbol)
        self._focus()
        with self._xlock:
            Xtst.XTestFakeKeyEvent(self._display, code, 1, 0)
            X11.XFlush(self._display)
            time.sleep(0.05)
            Xtst.XTestFakeKeyEvent(self._display, code, 0, 0)
            X11.XFlush(self._display)

    def _keycode(self, symbol):
        with self._xlock:
            code = X11.XKeysymToKeycode(self._display, symbol)
        if not code:
            raise RuntimeError(f"no keycode for keysym {hex(symbol)}")
        return code

    def _focus(self):
        if not self._win:
            return
        with self._xlock:
            # RevertToParent = 2. Focus has to be on the game or XTest
            # types into the player UI instead.
            X11.XSetInputFocus(self._display, self._win, 2, 0)
            X11.XFlush(self._display)
        time.sleep(0.05)

    def _warp(self, x_frac, y_frac):
        with self._xlock:
            rx, ry, width, height = _geometry(self._display, self._win)
            x = int(rx + x_frac * max(width - 1, 1))
            y = int(ry + y_frac * max(height - 1, 1))
            Xtst.XTestFakeMotionEvent(self._display, -1, x, y, 0)
            X11.XFlush(self._display)
        time.sleep(0.05)


def _fraction(value):
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("coordinate must be a number from 0 to 1") from exc
    if number < 0 or number > 1:
        raise ValueError("coordinate must be from 0 to 1")
    return number
