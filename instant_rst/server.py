from flask import Flask, render_template, request, url_for, jsonify, send_from_directory
from flask.ext.socketio import SocketIO, emit

import os, sys

from instant_rst.rst import html_body

from instant_rst.config import DEFAULT_FILE, SECRET_KEY,TEMPLATE_DIR,STATIC_DIR

app = Flask(__name__,
        static_folder=STATIC_DIR,
        template_folder=TEMPLATE_DIR)
# app.debug = True
app.config['SECRET_KEY'] = SECRET_KEY

socketio = SocketIO(app)

def run(port, template_dir, static_dir, images_dir):
    app.template_folder = template_dir
    app.static_folder = static_dir
    app.images_dir = images_dir
    socketio.run(app, port=port)

@app.route('/images/<name>')
def images(name):
    return send_from_directory(app.images_dir, name)


@app.route("/", methods=['GET','PUT','POST','DELETE'])
def index():
    if request.method == 'PUT' or request.method == 'POST':
        f = request.form.get('file', '')
        p = request.form.get('p', '-1')
        if os.path.isfile(f):
            with open(f,'r') as rst:
                d = html_body(rst.read().decode('utf8'))
            socketio.emit('updatingContent', {'HTML': d,'p':p})
            return jsonify(success='true',file=f, p=p)
        elif p != '-1':
            socketio.emit('updatingContent', {'p':p})
            return jsonify(success='true',file=f, p=p)
        else:
            return jsonify(success='false',info='File Not Exist',file=f)


    elif request.method == 'DELETE':

        socketio.emit('die', {'exit': 1})
        shutdown_server()

    elif request.method == 'GET':

        f = request.args.get('file', DEFAULT_FILE)
        if os.path.isfile(f):
            with open(f,'r') as rst:
                d = html_body(rst.read().decode('utf8'))
                return render_template('index.html',HTML=d)
        else:
            return render_template('index.html')

def shutdown_server():
    exit = request.environ.get('werkzeug.server.shutdown')
    if exit is None:
        sys.exit()
    exit()

@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})

