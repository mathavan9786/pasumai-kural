from flask import Flask, jsonify, render_template
from gtts import gTTS
import random, os, time

app = Flask(__name__)

def get_plant_stress():
    signals = [
        {"stress": "thirst", "level": random.randint(60, 90),
         "message": "உங்கள் பயிருக்கு தண்ணீர் தேவை. உடனே பாசனம் செய்யுங்கள்."},
        {"stress": "pest", "level": random.randint(70, 95),
         "message": "எச்சரிக்கை! பூச்சி தாக்குதல் கண்டறியப்பட்டது."},
        {"stress": "nutrient", "level": random.randint(40, 70),
         "message": "உங்கள் பயிருக்கு உரம் தேவை."},
        {"stress": "normal", "level": random.randint(10, 30),
         "message": "பயிர் ஆரோக்கியமாக உள்ளது."},
    ]
    return random.choice(signals)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/plant-status')
def plant_status():
    data = get_plant_stress()
    return jsonify(data)

@app.route('/api/voice-alert')
def voice_alert():
    data = get_plant_stress()
    tts = gTTS(text=data['message'], lang='ta')
    os.makedirs('static', exist_ok=True)
    tts.save('static/alert.mp3')
    return jsonify({"status": "generated", "message": data['message']})

if __name__ == '__main__':
    app.run(debug=True)