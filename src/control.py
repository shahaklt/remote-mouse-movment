# Map hand landmarks to mouse + WASD actions. Pure geometry; OS injection via pynput.

import numpy as np

WRIST, THUMB_TIP, INDEX_TIP, MIDDLE_TIP = 0, 4, 8, 12
INDEX_MCP, MIDDLE_MCP, PINKY_MCP = 5, 9, 17
WASD = ("w", "a", "s", "d")


def hand_scale(lm):
    return float(np.linalg.norm(lm[INDEX_MCP, :2] - lm[PINKY_MCP, :2])) + 1e-6


def pinch(lm, a, b, ratio=0.55):
    return float(np.linalg.norm(lm[a, :2] - lm[b, :2])) / hand_scale(lm) < ratio


def wasd_from_center(cx, cy, deadzone=0.12):
    keys = set()
    if cy < 0.5 - deadzone:
        keys.add("w")
    if cy > 0.5 + deadzone:
        keys.add("s")
    if cx < 0.5 - deadzone:
        keys.add("a")
    if cx > 0.5 + deadzone:
        keys.add("d")
    return keys


def cursor_target(x, y, screen_w, screen_h, margin=0.15):
    span = 1.0 - 2 * margin
    nx = min(max((x - margin) / span, 0.0), 1.0)
    ny = min(max((y - margin) / span, 0.0), 1.0)
    return int(round(nx * screen_w)), int(round(ny * screen_h))


def assign_roles(hands):
    # In the mirrored frame, the hand on the left half drives WASD, the right half drives the mouse.
    left = right = None
    for h in hands:
        cx = h["center"][0]
        if cx < 0.5:
            if left is None or cx < left["center"][0]:
                left = h
        elif right is None or cx > right["center"][0]:
            right = h
    return left, right


def screen_size():
    try:
        import tkinter as tk
        r = tk.Tk()
        r.withdraw()
        wh = (r.winfo_screenwidth(), r.winfo_screenheight())
        r.destroy()
        return wh
    except Exception:
        return 1920, 1080


class Controller:
    def __init__(self, inject=True, smoothing=0.5, screen=None):
        self.inject = inject
        self.smoothing = smoothing
        self.screen = screen or screen_size()
        self.held = set()
        self.left_down = False
        self.right_latched = False
        self.cursor = None
        self.mouse = self.keyboard = self.Button = None
        if inject:
            from pynput.mouse import Button, Controller as Mouse
            from pynput.keyboard import Controller as Keyboard
            self.mouse, self.keyboard, self.Button = Mouse(), Keyboard(), Button

    def update_wasd(self, left_hand):
        target = wasd_from_center(*left_hand["center"]) if left_hand else set()
        if self.inject:
            for k in target - self.held:
                self.keyboard.press(k)
            for k in self.held - target:
                self.keyboard.release(k)
        self.held = target
        return target

    def update_mouse(self, right_hand):
        events = []
        if not right_hand:
            self._set_left(False, events)
            return self.cursor, events
        lm = right_hand["lm"]
        tx, ty = cursor_target(lm[INDEX_TIP, 0], lm[INDEX_TIP, 1], *self.screen)
        if self.cursor is None:
            self.cursor = (tx, ty)
        else:
            s = self.smoothing
            self.cursor = (round(s * self.cursor[0] + (1 - s) * tx),
                           round(s * self.cursor[1] + (1 - s) * ty))
        if self.inject:
            self.mouse.position = self.cursor

        index_pinch = pinch(lm, THUMB_TIP, INDEX_TIP)
        middle_pinch = pinch(lm, THUMB_TIP, MIDDLE_TIP) and not index_pinch
        if index_pinch != self.left_down:
            self._set_left(index_pinch, events)
        if middle_pinch and not self.right_latched:
            if self.inject:
                self.mouse.click(self.Button.right)
            events.append("right-click")
            self.right_latched = True
        elif not middle_pinch:
            self.right_latched = False
        return self.cursor, events

    def _set_left(self, down, events):
        if down == self.left_down:
            return
        self.left_down = down
        if self.inject:
            (self.mouse.press if down else self.mouse.release)(self.Button.left)
        events.append("left-down" if down else "left-up")

    def release_all(self):
        if self.inject and self.keyboard:
            for k in self.held:
                self.keyboard.release(k)
            if self.left_down:
                self.mouse.release(self.Button.left)
        self.held = set()
        self.left_down = False
