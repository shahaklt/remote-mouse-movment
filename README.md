# Touchless Control: Hand Mouse + WASD Gaming

Control your computer with your bare hands over a webcam. Your right hand becomes the
mouse: move it to move the cursor, pinch your thumb and index finger to left click and
drag, pinch thumb and middle finger to right click. Your left hand becomes a WASD
joystick: move it up for W, down for S, left for A, right for D, so you can walk around
in a game while your right hand aims. Diagonals press two keys at once.

It is all geometry on the hand landmarks MediaPipe finds in each frame. No dataset, no
training, no GPU, no extra hardware beyond the webcam you already have.

## Run

```bash
pip install -r requirements.txt
python src/demo.py                          # control for real
python src/demo.py --no-inject              # track + on-screen HUD only, nothing moves
python src/demo.py --selftest --no-inject   # headless one-frame check
```

A window opens showing your camera with the hands drawn on top, a small WASD pad that
lights up, the cursor target, and click flashes. Press ESC to quit.

## Controls

| Hand | Gesture | Action |
|------|---------|--------|
| Right | move hand | move cursor |
| Right | pinch thumb + index | left click / drag |
| Right | pinch thumb + middle | right click |
| Left | hand up / down | W / S |
| Left | hand left / right | A / D |
| Left | hand in a corner | two keys, e.g. W + D |

## Notes

- Keep one hand on each side of the frame. The left half of the mirrored view drives
  WASD, the right half drives the mouse.
- Good lighting helps the tracker.
- Some games use DirectInput or anti-cheat that ignores simulated key presses. The
  controller works in desktop apps and many games, but not every game. See PROBLEMS.md.
- `--no-inject` is the safe way to try it without anything grabbing your real mouse.
