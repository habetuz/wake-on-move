#!/usr/bin/env python3
"""
Simple camera test - display video stream
Run with: LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libcamera/v4l2-compat.so python test.py
"""

import cv2
import sys

camera_index = 0

print(f"Opening camera {camera_index} with V4L2 backend...")
cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)

if not cap.isOpened():
    print(f"ERROR: Could not open camera {camera_index}")
    print("\nMake sure you run with:")
    print("  LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libcamera/v4l2-compat.so python test.py")
    sys.exit(1)

print("Camera opened! Testing frame read...")
ret, frame = cap.read()

if not ret:
    print("ERROR: Camera opened but cannot read frames")
    cap.release()
    sys.exit(1)

print(f"✓ SUCCESS! Camera is working")
print(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
print("\nDisplaying video stream. Press 'q' to quit.")

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        break
    
    frame_count += 1
    
    # Add frame counter to video
    cv2.putText(
        frame,
        f"Frame: {frame_count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )
    
    cv2.imshow('Camera Test - Press Q to quit', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"\nStreamed {frame_count} frames successfully!")

