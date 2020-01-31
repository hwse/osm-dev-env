#!/usr/bin/env python3


from flask import Flask, escape, request

app = Flask(__name__)


@app.route('/stage_2')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'
