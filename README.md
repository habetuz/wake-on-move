# wake-on-move

Motion detection application using webcam that triggers callbacks when movement is detected.

## Installation

```bash
bun install
```

## Usage

```bash
# Basic usage with default settings
bun start

# Specify camera device
bun start -- -d /dev/video0

# Set motion threshold (0.0-1.0, default: 0.02)
bun start -- -t 0.05

# Set capture interval in milliseconds (default: 1000)
bun start -- -i 500

# Enable video feed display in browser
bun start -- --show-video

# Use custom port for video feed
bun start -- --show-video 8080

# Combine multiple options
bun start -- -d /dev/video0 -t 0.03 -i 500 --show-video 3000
```

## Options

- `-d, --device <device>` - Camera device (e.g., /dev/video0 or false for default)
- `-t, --threshold <threshold>` - Motion detection threshold (0.0-1.0, default: 0.02)
- `-i, --interval <ms>` - Capture interval in milliseconds (default: 1000)
- `-s, --show-video [port]` - Display video feed in browser (default port: 3000)

## Project Structure

```
├── index.ts              # Main application entry point
├── src/
│   ├── motion-detector.ts # Motion detection logic
│   └── server.ts         # Web server for video display
└── public/
    ├── index.html        # Video feed UI
    ├── style.css         # Styles
    └── app.js            # Client-side JavaScript
```
