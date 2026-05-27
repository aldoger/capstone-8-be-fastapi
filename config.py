import os

class Config:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    CAMERA_SOURCE = "https://motchallenge.net/sequenceVideos/PETS09-S2L1-raw.mp4"
    YT_LIVESTREAM = False
    DISPLAY_WIDTH = 1280
    DISPLAY_HEIGHT = 720

    MODEL_PATH = os.path.join(PROJECT_ROOT, "v4.onnx")
    TARGET_CLASS_IDS = [1]
    INFERENCE_SIZE = (512, 512) # for v3.onnx model
    CONFIDENCE_THRESHOLD = 0.5
    ACTIVATE_TRACKER = True
    TRACKER = "OC-SORT"

# Notepad ===============================================================
# https://www.youtube.com/watch?v=UgrEsdDrZRM&t=114s 
# http://10.187.231.176:8080/video
# inference-test.mp4
# INFERENCE_SIZE = (384, 384) # for v1.sim.onnx model
# INFERENCE_SIZE = (672, 672) # for v2.onnx model