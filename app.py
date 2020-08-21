from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('client_event')
def client_msg():
    return None

@socketio.on('connect_event')
def connect_msg():
    return None

if __name__ == "__main__":
    socketio.run(app, debug=True, host='192.168.50.23', port=5000)