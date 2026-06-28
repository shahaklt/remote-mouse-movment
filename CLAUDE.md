# Touchless Control: Hand Mouse + WASD Gaming

## What This Is

A webcam-only, hands-free controller. The right hand moves the mouse and pinches to
click; the left hand acts as a WASD joystick so you can play games. No dataset, no
training, no special hardware. Rule-based MediaPipe hand landmarks on the live camera.

## How It Maps

Frame is mirrored (selfie view). Roles by screen side:
- Right hand (right half): index-fingertip position -> cursor. Thumb-index pinch =
  left click and drag (press on pinch, release on open). Thumb-middle pinch = right click.
- Left hand (left half): hand center vs a deadzone around frame center ->
  up=W, down=S, left=A, right=D. Diagonals press two keys (e.g., W+D).

OS input is injected with pynput. No GPU needed; MediaPipe runs on CPU.

## Science (verified)

- MediaPipe Hands real-time landmark tracking (Zhang et al. 2020, arXiv 2006.10214)
- Vision-based hand-gesture HCI / virtual mouse — verified via science_check.py

## Build Order (done)

1. src/hands.py — MediaPipe wrapper: frame -> per-hand 21 landmarks + center
2. src/control.py — pure geometry (wasd_from_center, pinch, cursor_target, assign_roles)
   and a Controller that injects mouse/keys via pynput
3. src/demo.py — real-time OpenCV loop: capture, mirror, track, control, draw HUD
4. tests/ — geometry + controller logic (no camera needed)
5. README.md — what it does, run, controls, caveats

## Run

    pip install -r requirements.txt
    python src/demo.py                 # plays for real
    python src/demo.py --no-inject     # track + HUD only, no mouse/keys moved
    python src/demo.py --selftest --no-inject   # one blank frame, headless check

## Demo Notes

This project's demo is a real-time OpenCV window, not Gradio: the point is injecting OS
mouse/keyboard while you watch your hands tracked. That is filmable and interactive,
which is what the demo rule is for. The HUD shows the tracked hands, the cursor target,
the active WASD keys, and click events.

## Caveats

- Some games use DirectInput / anti-cheat that ignores synthetic (SendInput) keys; the
  controller works in desktop apps and many games but not all. Documented in PROBLEMS.md.
- Needs reasonable lighting and one hand per side.

## Code Style

Functions not classes unless state requires it (Controller holds input state).
No docstrings on obvious functions. Names that say what the thing is.

## When Done

    python scripts/complete.py touchless-control "Touchless Control: Hand Mouse + WASD Gaming" \
      "Webcam hands-free controller: right hand mouse + pinch clicks, left hand WASD joystick."
