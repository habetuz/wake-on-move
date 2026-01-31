#!/usr/bin/env python3
"""
Simple camera test - try different backends to find what works
"""

import cv2
import sys

print("Testing camera access methods...\n")

# Test 1: Try V4L2 with LD_PRELOAD (should work with libcamera v4l2-compat)
print("=" * 50)
print("Test 1: V4L2 backend with different indices")
print("=" * 50)

for idx in range(10):
    print(f"\nTrying camera index {idx}...")
    cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"✓ SUCCESS! Camera {idx} works with V4L2")
            print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
            print(f"\nDisplaying video from camera {idx}. Press 'q' to quit.")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to read frame")
                    break
                
                cv2.imshow(f'Camera {idx} Test', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            print(f"\nCamera {idx} is working!")
            print(f"Use: --camera {idx} when running main.py")
            sys.exit(0)
        else:
            print(f"  Camera {idx} opened but cannot read frames")
            cap.release()
    else:
        print(f"  Camera {idx} failed to open")

print("\nNo working cameras found with V4L2 backend.")
print("\nMake sure you run this with:")
print("  LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libcamera/v4l2-compat.so python test.py")
