import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// Geliştirmede /api istekleri FastAPI'ye (8000) yönlendirilir; böylece tarayıcı tek adres görür.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
});
