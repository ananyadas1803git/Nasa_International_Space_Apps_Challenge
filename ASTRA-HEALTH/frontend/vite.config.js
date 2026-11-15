import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The dev server proxies /api and /health to the FastAPI backend, so the browser only ever talks to
// http://localhost:5173 - no CORS problems, no localhost-vs-127.0.0.1 mismatches.
const target = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': target, '/health': target } },
  preview: { port: 5173, proxy: { '/api': target, '/health': target } },
});
