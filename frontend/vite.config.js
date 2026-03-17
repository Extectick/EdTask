import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '0.0.0.0', // Доступ с локальной сети
    port: 5173,
    allowedHosts: [
      'hare.ge',
      'www.hare.ge',
      '37.233.82.200',
      'localhost',
      '127.0.0.1',
    ],
  }
})
