#!/usr/bin/env python3
"""
Motion Detection Screen Wake
"""

import cv2
import numpy as np
import os
import time
from datetime import datetime, timedelta


class MotionDetector:
    def __init__(
        self,
        threshold_sensitivity=25,
        min_area=500,
        wake_interval_seconds=10,
        blur_size=21,
        dry_run=False,
    ):
        """
        Initialize motion detector

        Args:
            threshold_sensitivity: Lower = more sensitive (0-255)
            min_area: Minimum pixel area to trigger motion detection
            wakup_interval_seconds: How often to send wake signal
            blur_size: Gaussian blur kernel size (odd number)
            dry_run: If True, only log motion without enabling screen
        """
        self.threshold_sensitivity = threshold_sensitivity
        self.min_area = min_area
        self.wakeup_interval_seconds = wake_interval_seconds
        self.blur_size = blur_size
        self.dry_run = dry_run

        self.last_motion_time = None
        self.first_frame = None
        self.camera = None
        self.dilation_kernel = np.ones((3, 3), dtype=np.uint8)
        self.no_motion_count = 0
        self.motion_count = 0

    def initialize_camera(self, camera_index=0):
        """Initialize the camera"""
        print(f"Attempting to open camera {camera_index}...")
        self.camera = cv2.VideoCapture(camera_index)
        print(f"VideoCapture object created")
        
        if not self.camera.isOpened():
            raise RuntimeError(f"Could not open camera {camera_index}")
        
        print(f"Camera opened, testing frame read...")
        # Test read a frame to ensure camera is actually working
        ret, frame = self.camera.read()
        if not ret:
            raise RuntimeError(f"Camera {camera_index} opened but cannot read frames")
        print(f"Frame read successful: {frame.shape}")
        
        # Let camera warm up
        time.sleep(1)
        print(f"Camera initialized (index: {camera_index})")

    def enable_screen(self):
        """Enable/wake the screen"""
        if self.dry_run:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] [DRY RUN] Would enable screen"
            )
            return

        try:
            command = "xset dpms force on"
            os.system(command)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Screen enabled")
        except Exception as e:
            print(f"Error enabling screen: {e}")

    def detect_motion(self, frame):
        """
        Detect motion in frame compared to baseline

        Returns:
            bool: True if motion detected
        """
        # Prepare frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (self.blur_size, self.blur_size), 0)

        # Initialize baseline frame
        if self.first_frame is None:
            self.first_frame = gray
            return False

        # Compute difference between current frame and baseline
        frame_delta = cv2.absdiff(self.first_frame, gray)
        thresh = cv2.threshold(
            frame_delta, self.threshold_sensitivity, 255, cv2.THRESH_BINARY
        )[1]

        # Dilate to fill holes
        thresh = cv2.dilate(thresh, self.dilation_kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Check if any contour is large enough
        for contour in contours:
            if cv2.contourArea(contour) >= self.min_area:
                return True

        return False

    def update_baseline(self, frame, motion_detected=False):
        """Update baseline frame for motion detection"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (self.blur_size, self.blur_size), 0)

        if self.first_frame is not None:
            # After 2 seconds of sustained motion (20 frames), replace baseline almost completely
            if self.motion_count > 20:
                # Aggressively reset baseline
                self.first_frame = cv2.addWeighted(self.first_frame, 0.1, gray, 0.9, 0)
            elif not motion_detected:
                # Adapt when no motion
                self.first_frame = cv2.addWeighted(self.first_frame, 0.7, gray, 0.3, 0)
            # Don't update baseline during active motion
        else:
            self.first_frame = gray

    def run(self, show_video=False):
        """
        Main loop for motion detection

        Args:
            show_video: If True, display video feed (for debugging)
        """
        if self.camera is None:
            raise RuntimeError(
                "Camera has not been initialized. Call initialize_camera() before run()."
            )
        print("Motion detector started")
        if self.dry_run:
            print("[DRY RUN MODE - no screen wake commands will be executed]")
        print(f"Screen timeout: {self.wakeup_interval_seconds} seconds")
        print(f"Sensitivity: {self.threshold_sensitivity}")
        print(f"Min area: {self.min_area}")
        print("Press Ctrl+C to quit")
        print("-" * 50)

        frame_count = 0
        screen_is_on = True

        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    print("Failed to read frame")
                    break

                frame_count += 1

                # Detect motion every frame
                motion_detected = self.detect_motion(frame)

                # Track motion over time
                if motion_detected:
                    self.motion_count += 1
                    self.no_motion_count = 0
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Motion detected!")
                    if (
                        self.last_motion_time is None
                        or datetime.now() - self.last_motion_time
                        > timedelta(seconds=self.wakeup_interval_seconds)
                    ):
                        self.last_motion_time = datetime.now()
                        self.enable_screen()
                else:
                    self.no_motion_count += 1
                    if self.no_motion_count > 100:
                        # Reset motion counter after sustained period of no motion
                        self.motion_count = 0

                # Update baseline frame every iteration
                self.update_baseline(frame, motion_detected)

                # Optional: Show video feed
                if show_video:
                    status_text = "MOTION" if motion_detected else "No motion"
                    color = (0, 0, 255) if motion_detected else (0, 255, 0)
                    cv2.putText(
                        frame,
                        status_text,
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        color,
                        2,
                    )

                    cv2.imshow("Motion Detector", frame)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                # Fast polling for quick motion detection
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nStopping motion detector...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Release camera and close windows"""
        # Turn screen back on when exiting
        self.enable_screen()

        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        print("Cleanup complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Motion detection screen wake")
    parser.add_argument(
        "--camera", type=int, default=0, help="Camera index (default: 0)"
    )
    parser.add_argument(
        "--sensitivity",
        type=int,
        default=25,
        help="Threshold sensitivity 0-255, lower=more sensitive (default: 25)",
    )
    parser.add_argument(
        "--min-area",
        type=int,
        default=500,
        help="Minimum motion area in pixels (default: 500)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="interval in seconds of how often a wake signal will be sent (default: 10)",
    )
    parser.add_argument(
        "--show-video", action="store_true", help="Show video feed for debugging"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log motion only, do not actually wake screen",
    )

    args = parser.parse_args()

    detector = MotionDetector(
        threshold_sensitivity=args.sensitivity,
        min_area=args.min_area,
        wake_interval_seconds=args.interval,
        dry_run=args.dry_run,
    )

    detector.initialize_camera(args.camera)
    detector.run(show_video=args.show_video)
