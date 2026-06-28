# Browser webcam HUD for Touchless Control. Run: python src/webapp.py -> http://localhost:7860
# Streams your webcam, tracks both hands, and draws the same HUD as the desktop demo.
# It does not move your real OS mouse/keys (a browser tab can't); it shows what the
# controller would do. Use src/demo.py for real OS injection.

import sys
from pathlib import Path

import cv2
import gradio as gr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hands import HandTracker
from control import Controller
from demo import step

tracker = HandTracker()
ctrl = Controller(inject=False)


def process(frame_rgb):
    if frame_rgb is None:
        return None
    bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    bgr = cv2.flip(bgr, 1)
    step(tracker, ctrl, bgr)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


with gr.Blocks(title="Touchless Control") as app:
    gr.Markdown(
        "# Touchless Control\n"
        "Right hand = mouse (pinch index = left click, middle = right click). "
        "Left hand = WASD. This browser view tracks and shows the HUD; it does not "
        "move your real mouse. Run `python src/demo.py` for that."
    )
    with gr.Row():
        cam = gr.Image(sources=["webcam"], streaming=True, label="camera")
        out = gr.Image(label="tracked")
    cam.stream(process, inputs=cam, outputs=out, stream_every=0.05)


if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=7860)
