from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def home():
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

    import random

    value = random.randint(30,80)

    return jsonify({"signal":value})


if __name__ == "__main__":
    app.run(debug=True)