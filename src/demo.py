# Real-time webcam controller. Run with `python src/demo.py`.
# Right hand moves the mouse (pinch index = left click, middle = right click).
# Left hand is a WASD joystick (up=W, down=S, left=A, right=D). ESC quits.

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cv2
from hands import HandTracker
from control import Controller, INDEX_TIP, assign_roles

HELP = "Right=mouse (pinch index=L, middle=R)   Left=WASD   ESC quits"
WASD_BOXES = {"w": (60, 44), "a": (28, 76), "s": (60, 76), "d": (92, 76)}


def draw_hud(frame, tracker, hands, left, right, keys, events):
    h, w = frame.shape[:2]
    for hand in hands:
        tracker.draw_landmarks(frame, hand)
    if left:
        cx, cy = left["center"]
        cv2.circle(frame, (int(cx * w), int(cy * h)), 9, (0, 255, 255), -1)
        cv2.putText(frame, "WASD", (int(cx * w) - 22, int(cy * h) - 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    if right:
        ix, iy = right["lm"][INDEX_TIP, 0], right["lm"][INDEX_TIP, 1]
        cv2.circle(frame, (int(ix * w), int(iy * h)), 9, (255, 140, 0), -1)
        cv2.putText(frame, "MOUSE", (int(ix * w) - 26, int(iy * h) - 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 140, 0), 2)
    for k, (x, y) in WASD_BOXES.items():
        on = k in keys
        cv2.rectangle(frame, (x, y), (x + 26, y + 26),
                      (0, 200, 0) if on else (70, 70, 70), -1 if on else 1)
        cv2.putText(frame, k.upper(), (x + 5, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 0, 0) if on else (200, 200, 200), 2)
    if events:
        cv2.putText(frame, "  ".join(events), (10, h - 18), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 0, 255), 2)
    cv2.putText(frame, HELP, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def step(tracker, ctrl, frame):
    hands = tracker.process(frame)
    left, right = assign_roles(hands)
    keys = ctrl.update_wasd(left)
    _, events = ctrl.update_mouse(right)
    draw_hud(frame, tracker, hands, left, right, keys, events)
    return hands, keys


def run(inject=True, camera=0, selftest=False):
    tracker = HandTracker()
    ctrl = Controller(inject=inject)
    if selftest:
        hands, keys = step(tracker, ctrl, np.zeros((480, 640, 3), np.uint8))
        print(f"selftest ok: hands={len(hands)} keys={keys} cursor={ctrl.cursor}")
        return
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        print(f"could not open camera {camera}")
        return
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            step(tracker, ctrl, frame)
            cv2.imshow("Touchless Control", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        ctrl.release_all()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-inject", action="store_true", help="track only, don't move the real mouse/keys")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--selftest", action="store_true", help="process one blank frame and exit")
    a = ap.parse_args()
    run(inject=not a.no_inject, camera=a.camera, selftest=a.selftest)
