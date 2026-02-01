import { Jimp } from 'jimp';
import pixelmatch from 'pixelmatch';

export class MotionDetector {
  private previousImage: Buffer | null = null;
  private threshold: number;

  constructor(threshold: number) {
    this.threshold = threshold;
  }

  async detectMotion(imageBuffer: Buffer): Promise<{ detected: boolean; percentage: number }> {
    const image = await Jimp.read(imageBuffer);
    const currentBuffer = Buffer.from(image.bitmap.data);

    if (!this.previousImage) {
      this.previousImage = currentBuffer;
      return { detected: false, percentage: 0 };
    }

    const width = image.bitmap.width;
    const height = image.bitmap.height;
    const diff = Buffer.alloc(width * height * 4);

    const numDiffPixels = pixelmatch(
      this.previousImage,
      currentBuffer,
      diff,
      width,
      height,
      { threshold: 0.1 }
    );

    const totalPixels = width * height;
    const diffPercentage = numDiffPixels / totalPixels;

    this.previousImage = currentBuffer;

    return {
      detected: diffPercentage > this.threshold,
      percentage: diffPercentage
    };
  }

  reset() {
    this.previousImage = null;
  }
}
