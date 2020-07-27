# camera.py

import cv2

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture("mov_hts-samp009.mp4")

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        ret, frame = cv2.imencode('.jpg', image)
        return frame.tobytes()