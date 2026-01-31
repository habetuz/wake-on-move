#!/usr/bin/env python3
"""
Simple camera test using Picamera2 (direct libcamera access)
Install with: pip install picamera2
"""

import cv2
import numpy as np

try:
    from picamera2 import Picamera2
except ImportError:
    print("ERROR: Picamera2 not installed")
    print("Install with: uv pip install picamera2")
    print("\nAlternatively: sudo apt install python3-picamera2")
    import sys
    sys.exit(1)

print("Listing available cameras...")
cameras = Picamera2.global_camera_info()
print(f"Found {len(cameras)} camera(s):")
for i, cam in enumerate(cameras):
    print(f"  {i}: {cam}")

if not cameras:
    print("ERROR: No cameras found")
    import sys
    sys.exit(1)

# Use first camera (usually front camera)
camera_index = 0
print(f"\nOpening camera {camera_index}...")

picam2 = Picamera2(camera_index)

# Configure for preview (lower resolution for better performance)
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)

print("Starting camera...")
picam2.start()

print("✓ SUCCESS! Camera is streaming")
print("Displaying video. Press 'q' to quit.")

frame_count = 0
try:
    while True:
        # Capture frame as numpy array (ready for OpenCV)
        frame = picam2.capture_array()
        
        # Convert RGB to BGR for OpenCV display
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        frame_count += 1
        
        # Add frame counter
        cv2.putText(
            frame_bgr,
            f"Frame: {frame_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        
        cv2.imshow('Camera Test - Press Q to quit', frame_bgr)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print(f"\nStreamed {frame_count} frames successfully!")


