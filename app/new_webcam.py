import cv2
import numpy
import time

class NWebcam():
    def __init__(self):
        self.dirname = ""
        self.cap = None
        self.camera = cv2.VideoCapture(0)    


    def gen_frames(self):
        while True:
            success, frame = self.camera.read()
            frame = cv2.flip(frame, 1)
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg',frame)
                frame = buffer.tobytes()
                yield(b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame +
                      b'\r\n')
        return frame
