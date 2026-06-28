# Problems

Log issues as P1, P2, ... Mark DONE when resolved.

## P1: handedness from MediaPipe flips with mirroring — DONE
MediaPipe's Left/Right label is unreliable once the frame is mirrored. Dropped it and
assign roles by screen side instead: left half of the mirrored view = WASD hand, right
half = mouse hand. Matches the user's own hands in selfie view.

## P2: cursor jitter — DONE
Index-fingertip position is noisy. Added exponential smoothing (smoothing=0.5) on the
cursor and a margin so the active hand region maps to the full screen.

## P3: left/right pinch ambiguity — DONE
Right click (thumb-middle) only fires when the index pinch is NOT active, and it is
edge-triggered (one click per pinch), so it never collides with left click/drag.

## P4: DirectInput / anti-cheat games ignore synthetic keys — OPEN (known limit)
pynput uses SendInput. Desktop apps and many games accept it, but some games read raw
DirectInput or run anti-cheat that ignores simulated input. A virtual-gamepad backend
(vgamepad) or an Interception driver would cover those; out of scope for v1.
