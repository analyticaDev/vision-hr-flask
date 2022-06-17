import sys
from flask import Flask, render_template, Response, send_file
import cv2

#ported
import sys
import time
import numpy
from process import Process
from webcam import Webcam

process = Process()

app = Flask(__name__)

# webcam = Webcam()
# process = Process()
# frame_np = numpy.zeros((10,10,3),numpy.uint8)

# frame = webcam.start()

# process.frame_in = frame
# process.run()

camera = cv2.VideoCapture(0)

def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            frame= cv2.flip(frame, 1)
            process.frame_in = frame
            process.run()
            frame = process.frame_out
            bpm = process.bpm
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.putText(frame, "FPS "+str(float("{:.2f}".format(process.fps))), (20, 460), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2)
            cv2.putText(frame, "BPM "+str(float("{:.2f}".format(bpm))), (200, 460), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2)
            # f_fr = cv2.cvtColor(f_fr,cv2.COLOR_RGB2BGR)
            # f_fr = numpy.transpose(f_fr, (0,1,2)).copy()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed')
def video_feed():
    #Video streaming route.
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/title-logo')
def title_logo():
    return send_file('VisionHR_logo.png', mimetype='image')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)