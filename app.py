import os
from flask import Flask, render_template, jsonify

# Template and Static folder-ah correct-ah point pannanum
app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static')

@app.route("/")
def home():
    return render_template("index.html")

# ... rest of your code (stats, signal) ...

if __name__ == "__main__":
    app.run(debug=True)