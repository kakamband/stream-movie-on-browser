from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
from flask_executor import Executor
from queue import Queue
import time
import base64

from camera import VideoCamera

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

app.config['EXECUTOR_TYPE'] = 'thread'
executor = Executor(app)
que = Queue()

socketIo = SocketIO(app, cors_allowed_origins="*")

app.debug = True
app.host = 'localhost'


@socketIo.on("start")
def start():
    executor.submit(event_polling, que)


def event_polling(q: Queue):
    '''キューからソケットに送るデータを取り出すループ'''
    while True:
        item = q.get()
        emit(item['command'], item['data'])


@app.route('/')
def index():
    return render_template('index.html')


def gen(camera):

    prefix = 'data:image/png;base64,'

    count = 0
    while True:
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        count += 1
        if frame is not None:
            if count % 45 == 0:
                # emit('capture-send', { 'dataURL': prefix+base64.b64encode(frame).decode('utf-8')})
                que.put({'count': count, 'command': 'capture-send',
                        'data': {'dataURL': prefix + base64.b64encode(frame).decode('utf-8')}})
                time.sleep(0.05)
        else:
            break


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    socketIo.run(app)
