# Libcamera Python Integration Guide for Microsoft Surface on Linux

## Summary of Findings

Since `qcam` works but OpenCV with v4l2-compat doesn't, you have several alternative approaches to access libcamera cameras in Python:

## Solution 1: Picamera2 (RECOMMENDED)

**Picamera2** is the official Python library for libcamera. Despite being developed for Raspberry Pi, it works on any Linux system with libcamera support.

### Installation

```bash
# Install libcamera and dependencies first
sudo apt install -y libcamera-dev libcamera-tools libcamera-ipa
sudo apt install -y python3-pip python3-libcamera python3-kms++
sudo apt install -y python3-pyqt5 python3-opengl python3-picamera2

# If python3-picamera2 is not available in your distro, install via pip:
pip install picamera2

# Install optional dependencies for full functionality
sudo apt install -y python3-opencv
pip install numpy pillow
```

### Basic Usage Examples

#### 1. Simple Image Capture

```python
#!/usr/bin/env python3
from picamera2 import Picamera2
import time

# Initialize camera
picam2 = Picamera2()

# Configure for still capture
config = picam2.create_still_configuration()
picam2.configure(config)

# Start camera
picam2.start()
time.sleep(2)  # Allow camera to warm up

# Capture image
picam2.capture_file("test.jpg")

# Stop camera
picam2.stop()
picam2.close()
```

#### 2. Video Stream with OpenCV Processing

```python
#!/usr/bin/env python3
from picamera2 import Picamera2
import cv2
import numpy as np

# Initialize camera
picam2 = Picamera2()

# Configure for preview (lower resolution for faster processing)
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)

picam2.start()

try:
    while True:
        # Capture frame as numpy array (compatible with OpenCV)
        frame = picam2.capture_array()
        
        # Process with OpenCV (example: convert to grayscale)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Display (optional)
        cv2.imshow("Camera", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
except KeyboardInterrupt:
    pass
finally:
    picam2.stop()
    cv2.destroyAllWindows()
```

#### 3. List Available Cameras

```python
#!/usr/bin/env python3
from picamera2 import Picamera2

# Get camera information
cameras = Picamera2.global_camera_info()

for idx, camera in enumerate(cameras):
    print(f"Camera {idx}:")
    print(f"  ID: {camera.get('Id', 'N/A')}")
    print(f"  Model: {camera.get('Model', 'N/A')}")
    print(f"  Location: {camera.get('Location', 'N/A')}")
    print()

# Use specific camera (0 for back, 1 for front on Surface)
picam2 = Picamera2(camera_num=0)  # Use camera_num to select
```

#### 4. Video Recording

```python
#!/usr/bin/env python3
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import time

picam2 = Picamera2()

# Create video configuration
video_config = picam2.create_video_configuration()
picam2.configure(video_config)

# Create encoder
encoder = H264Encoder(bitrate=10000000)

# Start recording
picam2.start_recording(encoder, 'output.h264')
time.sleep(10)  # Record for 10 seconds
picam2.stop_recording()

# Convert to MP4 (requires ffmpeg)
# ffmpeg -framerate 30 -i output.h264 -c copy output.mp4
```

---

## Solution 2: GStreamer Pipeline with OpenCV

If you want to use OpenCV's cv2.VideoCapture, use a GStreamer pipeline with libcamerasrc.

### Installation

```bash
sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-tools

# Ensure libcamera GStreamer plugin is installed
sudo apt install -y gstreamer1.0-libcamera
```

### Test GStreamer Pipeline

```bash
# List available cameras
gst-device-monitor-1.0 Video

# Test camera with display (if you have a display)
gst-launch-1.0 libcamerasrc ! videoconvert ! autovideosink

# Test specific resolution
gst-launch-1.0 libcamerasrc ! video/x-raw,width=640,height=480 ! videoconvert ! autovideosink
```

### OpenCV with GStreamer Pipeline

```python
#!/usr/bin/env python3
import cv2

# GStreamer pipeline for libcamera
# Adjust width, height, and framerate as needed
pipeline = (
    "libcamerasrc ! "
    "video/x-raw,width=640,height=480,framerate=30/1 ! "
    "videoconvert ! "
    "video/x-raw,format=BGR ! "
    "appsink drop=1"
)

# Open camera with GStreamer backend
cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Error: Could not open camera with GStreamer pipeline")
    exit(1)

print("Camera opened successfully with GStreamer")

try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to capture frame")
            break
        
        # Process frame
        cv2.imshow('Camera', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
except KeyboardInterrupt:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()
```

### Alternative GStreamer Pipelines

```python
# For MJPEG encoding (faster for some systems)
pipeline_mjpeg = (
    "libcamerasrc ! "
    "video/x-raw,width=640,height=480 ! "
    "jpegenc ! "
    "jpegdec ! "
    "videoconvert ! "
    "appsink"
)

# For higher resolution
pipeline_hd = (
    "libcamerasrc ! "
    "video/x-raw,width=1280,height=720,framerate=30/1 ! "
    "videoconvert ! "
    "video/x-raw,format=BGR ! "
    "appsink drop=1"
)

# Specify camera by name (if you have multiple cameras)
pipeline_named = (
    'libcamerasrc camera-name="\\_SB_.PCI0.I2C2.CAMR" ! '
    "video/x-raw,width=640,height=480 ! "
    "videoconvert ! "
    "appsink"
)
```

---

## Solution 3: Python libcamera Bindings (Advanced)

For direct libcamera API access, use the Python bindings.

### Installation

```bash
# Usually installed with libcamera
sudo apt install -y python3-libcamera

# Or build from source if needed
```

### Basic Example

```python
#!/usr/bin/env python3
import libcamera
import time

# Create camera manager
cm = libcamera.CameraManager.singleton()

# List cameras
cameras = cm.cameras
for idx, camera in enumerate(cameras):
    print(f"Camera {idx}: {camera.id}")

# Get first camera
if len(cameras) > 0:
    camera = cameras[0]
    
    # Acquire camera
    camera.acquire()
    
    # Configure camera
    config = camera.generate_configuration([libcamera.StreamRole.Viewfinder])
    camera.configure(config)
    
    # Release camera
    camera.release()

print("Done")
```

**Note:** Direct libcamera Python bindings are more complex and less documented. Use Picamera2 for easier development.

---

## Solution 4: Check for v4l2loopback Alternative

If you really need V4L2 compatibility, try creating a V4L2 loopback device fed by libcamera.

```bash
# Install v4l2loopback
sudo apt install -y v4l2loopback-dkms v4l2loopback-utils

# Load module
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="libcamera" exclusive_caps=1

# Feed libcamera to v4l2loopback using GStreamer
gst-launch-1.0 libcamerasrc ! videoconvert ! v4l2sink device=/dev/video10

# Then use /dev/video10 with OpenCV
```

```python
import cv2

cap = cv2.VideoCapture(10)  # Use the loopback device
```

---

## Known Issues with Surface Devices

1. **V4L2 Backend Issues**: Surface cameras often use proprietary interfaces that don't work well with standard V4L2. This is why v4l2-compat with libcamera fails.

2. **Camera Names**: Surface cameras have unusual ACPI names like `\_SB_.PCI0.I2C2.CAMR`. Use these names when specifying cameras in GStreamer.

3. **Resolution Support**: Some Surface cameras have limited resolution support. Check available resolutions:

```bash
libcamera-hello --list-cameras
```

4. **Permission Issues**: Ensure your user is in the `video` group:

```bash
sudo usermod -a -G video $USER
# Log out and back in
```

---

## Troubleshooting

### Check libcamera Installation

```bash
# Test libcamera directly
libcamera-hello --list-cameras

# Test with qcam (you already know this works)
qcam

# Check GStreamer plugins
gst-inspect-1.0 libcamerasrc
```

### Debug OpenCV GStreamer Support

```python
import cv2
print(cv2.getBuildInformation())
# Look for GStreamer: YES
```

### Build OpenCV with GStreamer Support

If OpenCV doesn't have GStreamer support:

```bash
# Install dependencies
sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev

# Rebuild OpenCV with GStreamer support
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python --no-binary opencv-python
```

---

## Complete Working Example for Surface Device

```python
#!/usr/bin/env python3
"""
Complete camera streaming example for Microsoft Surface with libcamera
Tries multiple methods in order of preference
"""

import sys

def method_picamera2():
    """Method 1: Picamera2 (RECOMMENDED)"""
    try:
        from picamera2 import Picamera2
        import cv2
        
        print("Trying Picamera2...")
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
        picam2.configure(config)
        picam2.start()
        
        print("Picamera2 started successfully!")
        while True:
            frame = picam2.capture_array()
            cv2.imshow('Picamera2', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        picam2.stop()
        cv2.destroyAllWindows()
        return True
        
    except Exception as e:
        print(f"Picamera2 failed: {e}")
        return False

def method_gstreamer():
    """Method 2: OpenCV with GStreamer"""
    try:
        import cv2
        
        print("Trying GStreamer pipeline...")
        pipeline = (
            "libcamerasrc ! "
            "video/x-raw,width=640,height=480,framerate=30/1 ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink drop=1"
        )
        
        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        
        if not cap.isOpened():
            raise Exception("Could not open GStreamer pipeline")
        
        print("GStreamer pipeline opened successfully!")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2.imshow('GStreamer', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return True
        
    except Exception as e:
        print(f"GStreamer failed: {e}")
        return False

def main():
    print("Testing libcamera access methods for Surface device...\n")
    
    # Try methods in order of preference
    if method_picamera2():
        print("\n✓ Picamera2 works!")
        return
    
    if method_gstreamer():
        print("\n✓ GStreamer works!")
        return
    
    print("\n✗ All methods failed. Please check:")
    print("  1. Is libcamera installed? (libcamera-hello --list-cameras)")
    print("  2. Does qcam work?")
    print("  3. Are you in the video group? (groups | grep video)")
    print("  4. Is picamera2 installed? (pip install picamera2)")
    print("  5. Does OpenCV have GStreamer support? (check cv2.getBuildInformation())")
    sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Recommended Approach for Your Project

Based on your setup where `qcam` works:

1. **Install Picamera2**: `pip install picamera2`
2. **Use the simple capture API** shown in the examples above
3. **Convert frames to OpenCV format** when needed using `.capture_array()`
4. **Fall back to GStreamer pipeline** if Picamera2 has issues

This avoids the v4l2-compat issues entirely while maintaining full libcamera functionality.
