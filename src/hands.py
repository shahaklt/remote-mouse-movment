# MediaPipe Tasks HandLandmarker wrapper: BGR frame -> per-hand 21 landmarks + center.

import urllib.request
from pathlib import Path

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

MIDDLE_MCP = 9
MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
             "hand_landmarker/float16/1/hand_landmarker.task")
MODEL_PATH = Path(__file__).resolve().parent / "models" / "hand_landmarker.task"

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]


def ensure_model():
    if not MODEL_PATH.exists():
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        print("downloading hand_landmarker.task ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return str(MODEL_PATH)


class HandTracker:
    def __init__(self, max_hands=2, det=0.6):
        opts = vision.HandLandmarkerOptions(
            base_options=mp_tasks.BaseOptions(model_asset_path=ensure_model()),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=max_hands,
            min_hand_detection_confidence=det,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(opts)

    def process(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        res = self.landmarker.detect(image)
        out = []
        for hand in res.hand_landmarks:
            lm = np.array([[p.x, p.y, p.z] for p in hand], dtype=np.float32)
            out.append({"lm": lm, "center": (float(lm[MIDDLE_MCP, 0]), float(lm[MIDDLE_MCP, 1]))})
        return out

    def draw_landmarks(self, frame, hand):
        h, w = frame.shape[:2]
        lm = hand["lm"]
        for a, b in HAND_CONNECTIONS:
            pa = (int(lm[a, 0] * w), int(lm[a, 1] * h))
            pb = (int(lm[b, 0] * w), int(lm[b, 1] * h))
            cv2.line(frame, pa, pb, (0, 200, 0), 2)
        for p in lm:
            cv2.circle(frame, (int(p[0] * w), int(p[1] * h)), 3, (0, 0, 255), -1)
