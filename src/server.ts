import fs from 'fs';
import path from 'path';

export function startVideoServer(port: number, getLatestFrame: () => Buffer | null, isMotionDetected: () => boolean, captureInterval: number) {
  // Get the project root directory (parent of src)
  const projectRoot = path.join(import.meta.dir, '..');
  
  const server = Bun.serve({
    port,
    fetch(req) {
      const url = new URL(req.url);
      
      // Serve static files from public directory
      if (url.pathname === '/') {
        const html = fs.readFileSync(path.join(projectRoot, 'public', 'index.html'), 'utf-8');
        return new Response(html, { headers: { 'Content-Type': 'text/html' } });
      }
      
      if (url.pathname === '/style.css') {
        const css = fs.readFileSync(path.join(projectRoot, 'public', 'style.css'), 'utf-8');
        return new Response(css, { headers: { 'Content-Type': 'text/css' } });
      }
      
      if (url.pathname === '/app.js') {
        let js = fs.readFileSync(path.join(projectRoot, 'public', 'app.js'), 'utf-8');
        // Inject capture interval into the JS
        js = js.replace('1000', captureInterval.toString());
        return new Response(js, { headers: { 'Content-Type': 'application/javascript' } });
      }
      
      // API endpoints
      if (url.pathname === '/frame.jpg') {
        const frame = getLatestFrame();
        if (frame) {
          return new Response(frame, { headers: { 'Content-Type': 'image/jpeg' } });
        }
        return new Response('No frame available', { status: 404 });
      }
      
      if (url.pathname === '/status') {
        return new Response(JSON.stringify({ motion: isMotionDetected() }), {
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      return new Response('Not found', { status: 404 });
    }
  });
  
  console.log(`Video feed available at: http://localhost:${port}`);
  return server;
}
