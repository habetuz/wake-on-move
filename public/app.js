const img = document.getElementById('feed');
const status = document.getElementById('status');

// Get capture interval from server config
const CAPTURE_INTERVAL = parseInt(new URLSearchParams(window.location.search).get('interval') || '1000');

setInterval(async () => {
  try {
    const response = await fetch('/frame.jpg?t=' + Date.now());
    if (response.ok) {
      const blob = await response.blob();
      img.src = URL.createObjectURL(blob);
    }
    
    const statusResponse = await fetch('/status');
    const data = await statusResponse.json();
    status.textContent = data.motion ? 'MOTION DETECTED' : 'No Motion';
    status.className = data.motion ? 'motion' : 'no-motion';
  } catch (e) {
    console.error('Error fetching frame:', e);
  }
}, CAPTURE_INTERVAL);
