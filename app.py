import os
import random
from flask import Flask, render_template, jsonify

# Path-ah fix panrom so that Vercel can find the files
template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

@app.route("/")
def home():
    print("Home route hit!") 
    return render_template("index.html")

@app.route("/stats")
def stats():
    data = {
        "total": 24,
        "healthy": 17,
        "warning": 3,
        "critical": 0
    }
    return jsonify(data)

@app.route("/signal")
def signal():
    value = random.randint(30, 80)
    return jsonify({"signal": value})

# Vercel deployment-ku idhu romba mukkiyam
if __name__ == "__main__":
    app.run(debug=True)