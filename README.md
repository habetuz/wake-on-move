# wake-on-motion

> [!WARNING]
> This software was completely vibe coded. Use at your own risk.

## Why?

I built this for my Microsoft Surface dashboard that should wake up using its camera when someone is approaching it. Instead of having the screen constantly on or requiring manual interaction, the camera detects motion and automatically wakes the display.

## Usage

### Installation

Requires Python 3 with OpenCV:

```bash
pip install opencv-python numpy
```

### Running

Basic usage:

```bash
python main.py
```

### Options

```
--camera INDEX          Camera index (default: 0)
--sensitivity VALUE     Threshold sensitivity 0-255, lower=more sensitive (default: 25)
--min-area PIXELS       Minimum motion area in pixels (default: 500)
--interval SECONDS      How often to send wake signal when motion detected (default: 10)
--show-video            Show video feed for debugging
--dry-run               Log motion only, don't actually wake screen
```

### Examples

Test without waking the screen:

```bash
python main.py --dry-run --show-video
```

Run with higher sensitivity:

```bash
python main.py --sensitivity 15
```

Use specific camera:

```bash
python main.py --camera 1
```

### How it works

- Monitors camera feed for motion using frame differencing
- When motion is detected, sends `xset dpms force on` to wake the display
- Adaptively updates the baseline frame to handle lighting changes and stop detecting stationary objects
- Motion detection stops ~2-3 seconds after you stop moving

Press `Ctrl+C` to stop.

