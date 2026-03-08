Copy

from flask import Flask, jsonify, render_template_string
from gtts import gTTS
import random, os, io, base64
import urllib.request
import json

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def save_to_supabase(data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/plant_alerts"
        payload = json.dumps({
            "stress": data["stress"],
            "level": data["level"],
            "message": data["message"]
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("apikey", SUPABASE_KEY)
        req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
        req.add_header("Prefer", "return=minimal")
        req.add_header("X-Supabase-Api-Version", "2024-01-01")
        with urllib.request.urlopen(req) as res:
            print(f"Saved OK: {res.status}")
    except Exception as e:
        print(f"Save error: {e}")

def get_history():
    try:
        url = f"{SUPABASE_URL}/rest/v1/plant_alerts?select=*&order=created_at.desc&limit=10"
        req = urllib.request.Request(url, method="GET")
        req.add_header("apikey", SUPABASE_KEY)
        req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())
    except Exception as e:
        print(f"Fetch error: {e}")
        return []

def get_plant_stress():
    signals = [
        {"stress": "thirst", "level": random.randint(60, 90), "emoji": "💧",
         "message": "உங்கள் பயிருக்கு தண்ணீர் தேவை. உடனே பாசனம் செய்யுங்கள்."},
        {"stress": "pest", "level": random.randint(70, 95), "emoji": "🐛",
         "message": "எச்சரிக்கை! பூச்சி தாக்குதல் கண்டறியப்பட்டது. பூச்சிக்கொல்லி தெளிக்கவும்."},
        {"stress": "nutrient", "level": random.randint(40, 70), "emoji": "🌿",
         "message": "உங்கள் பயிருக்கு உரம் தேவை. உரமிடவும்."},
        {"stress": "normal", "level": random.randint(10, 30), "emoji": "✅",
         "message": "பயிர் ஆரோக்கியமாக உள்ளது. தொடர்ந்து கவனிக்கவும்."},
    ]
    return random.choice(signals)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>பசுமை குரல் 🌱</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #e8f5e9, #c8e6c9); min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 20px; }
    h1 { color: #2e7d32; font-size: 2rem; margin: 20px 0 4px; }
    p.sub { color: #666; font-size: 0.95rem; margin-bottom: 24px; }
    .card { background: white; border-radius: 20px; padding: 30px; max-width: 520px; width: 100%; box-shadow: 0 10px 40px rgba(0,0,0,0.12); margin-bottom: 20px; }
    .card h2 { color: #2e7d32; margin-bottom: 14px; font-size: 1.1rem; }
    .status-box { background: #f1f8e9; border-radius: 14px; padding: 20px; display: none; margin-bottom: 16px; text-align: center; }
    .emoji { font-size: 2.5rem; margin-bottom: 8px; }
    .message { font-size: 1.1rem; color: #1b5e20; font-weight: 600; line-height: 1.6; }
    .level-bar-bg { background: #dcedc8; border-radius: 20px; height: 12px; width: 100%; overflow: hidden; margin-top: 12px; }
    .level-bar { height: 100%; border-radius: 20px; background: linear-gradient(90deg, #66bb6a, #ff7043); transition: width 0.6s ease; }
    .level-text { font-size: 0.82rem; color: #888; margin-top: 4px; }
    .btn { background: #2e7d32; color: white; border: none; padding: 12px 24px; border-radius: 30px; font-size: 0.95rem; cursor: pointer; margin: 6px; transition: background 0.3s; }
    .btn:hover { background: #1b5e20; }
    .btn:disabled { background: #aaa; cursor: not-allowed; }
    .btn-voice { background: #1565c0; }
    .btn-voice:hover { background: #0d47a1; }
    audio { margin-top: 12px; width: 100%; display: none; }
    .history-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .history-table th { background: #e8f5e9; color: #2e7d32; padding: 8px; text-align: left; }
    .history-table td { padding: 8px; border-bottom: 1px solid #f0f0f0; color: #444; }
    .badge { padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: bold; }
    .thirst { background: #e3f2fd; color: #1565c0; }
    .pest { background: #fce4ec; color: #c62828; }
    .nutrient { background: #f3e5f5; color: #6a1b9a; }
    .normal { background: #e8f5e9; color: #2e7d32; }
    .loading { color: #888; font-size: 0.88rem; margin-top: 8px; display: none; }
  </style>
</head>
<body>
  <h1>🌱 பசுமை குரல்</h1>
  <p class="sub">AI-Powered Plant Health Monitoring | பயிர் உடல்நல கண்காணிப்பு</p>
  <div class="card">
    <h2>🌿 பயிர் நிலை</h2>
    <div class="status-box" id="statusBox">
      <div class="emoji" id="emoji"></div>
      <div class="message" id="message"></div>
      <div class="level-bar-bg"><div class="level-bar" id="levelBar" style="width:0%"></div></div>
      <div class="level-text" id="levelText"></div>
    </div>
    <audio id="alertAudio" controls></audio>
    <div>
      <button class="btn" onclick="checkStatus()">🔍 பயிர் நிலை பார்</button>
      <button class="btn btn-voice" id="voiceBtn" onclick="getVoice()">🔊 குரல் அறிவிப்பு</button>
    </div>
    <div class="loading" id="loading">⏳ ஒரு நிமிடம்...</div>
  </div>
  <div class="card">
    <h2>📋 கடந்த 10 Alerts (Database History)</h2>
    <button class="btn" onclick="loadHistory()" style="margin-bottom:14px;">🔄 Refresh History</button>
    <table class="history-table">
      <thead><tr><th>நிலை</th><th>Level</th><th>நேரம்</th></tr></thead>
      <tbody id="historyBody"><tr><td colspan="3" style="text-align:center;color:#aaa;">Load பண்ணவும்...</td></tr></tbody>
    </table>
  </div>
  <script>
    async function checkStatus() {
      document.getElementById('loading').style.display = 'block';
      const res = await fetch('/api/plant-status');
      const data = await res.json();
      document.getElementById('loading').style.display = 'none';
      document.getElementById('statusBox').style.display = 'block';
      document.getElementById('emoji').innerText = data.emoji;
      document.getElementById('message').innerText = data.message;
      document.getElementById('levelBar').style.width = data.level + '%';
      document.getElementById('levelText').innerText = 'Alert Level: ' + data.level + '%';
      setTimeout(loadHistory, 1500);
    }
    async function getVoice() {
      const btn = document.getElementById('voiceBtn');
      btn.disabled = true; btn.innerText = '⏳ உருவாக்குகிறோம்...';
      document.getElementById('loading').style.display = 'block';
      const res = await fetch('/api/voice-alert');
      const data = await res.json();
      document.getElementById('loading').style.display = 'none';
      btn.disabled = false; btn.innerText = '🔊 குரல் அறிவிப்பு';
      if (data.audio_base64) {
        const audio = document.getElementById('alertAudio');
        audio.src = 'data:audio/mp3;base64,' + data.audio_base64;
        audio.style.display = 'block';
        audio.play();
        document.getElementById('statusBox').style.display = 'block';
        document.getElementById('emoji').innerText = data.emoji;
        document.getElementById('message').innerText = data.message;
        document.getElementById('levelBar').style.width = data.level + '%';
        document.getElementById('levelText').innerText = 'Alert Level: ' + data.level + '%';
      }
      setTimeout(loadHistory, 1500);
    }
    async function loadHistory() {
      const res = await fetch('/api/history');
      const rows = await res.json();
      const tbody = document.getElementById('historyBody');
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#aaa;">No data yet</td></tr>';
        return;
      }
      tbody.innerHTML = rows.map(r => {
        const date = new Date(r.created_at).toLocaleString('ta-IN');
        return `<tr><td><span class="badge ${r.stress}">${r.stress}</span></td><td>${r.level}%</td><td>${date}</td></tr>`;
      }).join('');
    }
    loadHistory();
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/plant-status')
def plant_status():
    data = get_plant_stress()
    save_to_supabase(data)
    return jsonify(data)

@app.route('/api/voice-alert')
def voice_alert():
    try:
        data = get_plant_stress()
        tts = gTTS(text=data['message'], lang='ta')
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)
        audio_base64 = base64.b64encode(mp3_buffer.read()).decode('utf-8')
        save_to_supabase(data)
        return jsonify({"status": "success", "message": data['message'],
                        "stress": data['stress'], "emoji": data['emoji'],
                        "level": data['level'], "audio_base64": audio_base64})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/history')
def history():
    return jsonify(get_history())

@app.route('/api/debug')
def debug():
    return jsonify({
        "supabase_url": SUPABASE_URL,
        "key_set": bool(SUPABASE_KEY),
        "key_prefix": SUPABASE_KEY[:25] if SUPABASE_KEY else "NOT SET"
    })

app = app






