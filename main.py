from flask import Flask, render_template,request
from pathlib import Path

import os
import flask_monitoringdashboard as dashboard

app = Flask(__name__, static_folder="static")
dashboard.bind(app)

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["inputFile"]
        if not file.filename.lower().endswith((".mp3",".wav")):
                return "Mauvais format"
        elif Path(f"static/music/{file.filename}").is_file():
                return "Cette musique existe déjà"

        file.save(f"static/music/{file.filename}")
        return f"Musique envoyée {file.filename}"
    except Exception as e:
        return f"Erreur lors de l'envoi : {e}"

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/music")
def music():
    musicList = []
    files = os.listdir("static/music")
    for f in files:
        musicList.append(f)
    return render_template("music.html", musicList=musicList)
