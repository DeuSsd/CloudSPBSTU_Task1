from crypt import methods
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world():
    return "<p>Hello, World!</p>\n"

@app.route("/change_password", methods=['PUT'] )
def change_password():
    return f"<p>new password is {request.form['password']}!</p>\n"

@app.route("/login", methods=['POST'])
def login():
    return f"<p>Your Login is {request.form['username']}</p>\n"

app.run(host='0.0.0.0', port=5000)