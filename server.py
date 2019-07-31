from flask import Flask, send_from_directory, jsonify, request
import os
import shutil
import random

from settings import *
from parallel_bible import ParallelBible

app = Flask(__name__)
modules = [ m[:-4] for m in os.listdir(MODULES_PATH) if m.endswith(".zip") ]

@app.route("/modules")
def send_modules():
    return jsonify({"modules" : modules})

@app.route("/res/<path:path>")
def send_res(path):
    return send_from_directory(RES_PATH, path)

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory(STATIC_PATH, path)

@app.route("/generate")
def generate():
    m1, m2 = request.args['left'], request.args['right']
    pb = ParallelBible(m1, m2)
    random_str = str(random.randint(10**10, 10**11))
    path = TMP_PATH + random_str + os.sep
    name = m1 + "_" + m2 + "_" + random_str
    pb.save_epub(name, path, res_path=RES_PATH)
    return jsonify({ "res": name })

@app.route("/favicon.ico")
def send_favicon():
    return send_from_directory(STATIC_PATH, "favicon.ico")

@app.route("/")
def send_index():
    return send_from_directory(STATIC_PATH, "index.html")

if __name__ == "__main__":
    app.run()
