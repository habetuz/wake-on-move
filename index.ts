import NodeWebcam from 'node-webcam';
import { program } from 'commander';
import { MotionDetector } from './src/motion-detector';
import { startVideoServer } from './src/server';

// Parse command line arguments
program
  .option('-d, --device <device>', 'camera device (e.g., /dev/video0 or false for default)', 'false')
  .option('-t, --threshold <threshold>', 'motion detection threshold (0.0-1.0)', '0.02')
  .option('-i, --interval <ms>', 'capture interval in milliseconds', '1000')
  .option('-s, --show-video [port]', 'display video feed in browser (default port: 3000)', false)
  .parse();

const options = program.opts();

// Parse options
const device = options.device === 'false' ? false : options.device;
const MOTION_THRESHOLD = parseFloat(options.threshold);
const CAPTURE_INTERVAL = parseInt(options.interval);
const SHOW_VIDEO = options.showVideo !== false;
const VIDEO_PORT = typeof options.showVideo === 'string' ? parseInt(options.showVideo) : 3000;

// Configure webcam
const opts = {
  width: 640,
  height: 480,
  quality: 80,
  frames: 20,
  delay: 0,
  greyscale: "true",
  saveShots: false,
  output: "jpeg",
  device: device,
  callbackReturn: "buffer",
  verbose: false,
  setValues: {
    skip: "19",
  },
} as NodeWebcam.WebcamOptions;

const Webcam = NodeWebcam.create(opts);

// Initialize motion detector
const motionDetector = new MotionDetector(MOTION_THRESHOLD);
let latestFrame: Buffer | null = null;
let motionDetected = false;

// Callback function triggered when motion is detected
function onMotionDetected(diffPercentage: number) {
  console.log(`MOTION DETECTED! Difference: ${(diffPercentage * 100).toFixed(2)}%`);
  // Add your custom logic here
}

async function captureAndDetectMotion() {
  Webcam.capture('', async (err, data) => {
    if (err) {
      console.error('Error capturing photo:', err);
      return;
    }

    try {
      const imageBuffer = data as Buffer;
      
      // Store latest frame for video display
      if (SHOW_VIDEO) {
        latestFrame = imageBuffer;
      }

      // Detect motion
      const result = await motionDetector.detectMotion(imageBuffer);
      
      if (result.detected) {
        motionDetected = true;
        onMotionDetected(result.percentage);
      } else {
        motionDetected = false;
        console.log(`No motion (${(result.percentage * 100).toFixed(2)}% changed)`);
      }
    } catch (error) {
      console.error('Error processing image:', error);
    }
  });
}

// Capture and analyze at the specified interval
setInterval(captureAndDetectMotion, CAPTURE_INTERVAL);

// Start HTTP server if --show-video is enabled
if (SHOW_VIDEO) {
  startVideoServer(
    VIDEO_PORT,
    () => latestFrame,
    () => motionDetected,
    CAPTURE_INTERVAL
  );
}

console.log(`Starting motion detection...`);
console.log(`Device: ${device === false ? 'default' : device}`);
console.log(`Motion threshold: ${(MOTION_THRESHOLD * 100).toFixed(2)}%`);
console.log(`Capture interval: ${CAPTURE_INTERVAL}ms`);