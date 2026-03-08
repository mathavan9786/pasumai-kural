from flask import Flask, jsonify, render_template_string
from gtts import gTTS
import io
import base64
import os
import json
import urllib.request

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# -----------------------------
# Save data to Supabase
# -----------------------------
def save_to_supabase(stress, level, message):

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase key missing")
        return

    url = f"{SUPABASE_URL}/rest/v1/plant_alerts"

    data = json.dumps({
        "stress": stress,
        "level": level,
        "message": message
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data)

    req.add_header("Content-Type", "application/json")
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Prefer", "return=minimal")

    try:
        urllib.request.urlopen(req)
        print("Saved to Supabase")
    except Exception as e:
        print("Save error:", e)


# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():

    html = """
    <h1>🌱 பசுமை குரல்</h1>

    <button onclick="checkPlant()">பயிர் நிலை பார்</button>
    <button onclick="loadHistory()">Refresh History</button>

    <pre id="result"></pre>

    <h3>History</h3>
    <pre id="history"></pre>

<script>

async function checkPlant(){

const res = await fetch('/api/plant-status')
const data = await res.json()

document.getElementById("result").innerText =
JSON.stringify(data,null,2)

}

async function loadHistory(){

const res = await fetch('/api/history')
const data = await res.json()

document.getElementById("history").innerText =
JSON.stringify(data,null,2)

}

</script>
"""

    return render_template_string(html)


# -----------------------------
# Plant Status API
# -----------------------------
@app.route("/api/plant-status")
def plant_status():

    stress = "pest"
    level = 92
    message = "எச்சரிக்கை! பூச்சி தாக்குதல் கண்டறியப்பட்டது."

    save_to_supabase(stress, level, message)

    return jsonify({
        "stress": stress,
        "level": level,
        "message": message
    })


# -----------------------------
# History API
# -----------------------------
@app.route("/api/history")
def history():

    url = f"{SUPABASE_URL}/rest/v1/plant_alerts?select=*"

    req = urllib.request.Request(url)

    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")

    try:

        res = urllib.request.urlopen(req)
        data = json.loads(res.read())

        return jsonify(data)

    except Exception as e:

        return jsonify({"error": str(e)})


# -----------------------------
# Voice Alert API
# -----------------------------
@app.route("/api/voice-alert")
def voice_alert():

    text = "உங்கள் பயிருக்கு கவனம் தேவை"

    tts = gTTS(text=text, lang="ta")

    fp = io.BytesIO()
    tts.write_to_fp(fp)

    audio_base64 = base64.b64encode(fp.getvalue()).decode()

    return jsonify({
        "audio": audio_base64
    })


# -----------------------------
# Debug
# -----------------------------
@app.route("/api/debug")
def debug():

    return jsonify({
        "key_set": bool(SUPABASE_KEY),
        "supabase_url": SUPABASE_URL
    })


app.run()