from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# Route for Home Page
@app.route('/')
def index():
    return render_template('index.html')

# API for Bio-Signal (Returns random 30-80)
@app.route('/signal')
def get_signal():
    return jsonify({"signal": random.randint(30, 80)})

# API for Map (Returns list of 15 statuses: 0=Red, 1=Green, 2=Orange)
@app.route('/get_map_data')
def get_map_data():
    data = [random.randint(0, 2) for _ in range(15)]
    return jsonify({"map": data})

if __name__ == '__main__':
    app.run(debug=True)