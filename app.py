from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('control.html')

if __name__ == "__main__":
    app.run(debug=True)