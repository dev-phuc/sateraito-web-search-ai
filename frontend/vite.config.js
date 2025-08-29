import { defineConfig, loadEnv } from 'vite'
import { fileURLToPath, URL } from 'node:url'
import { resolve } from "path";

import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const now = new Date();
const timestamp = now.getTime();
const version = timestamp;

// https://vite.dev/config/
export default ({ mode }) => {
  process.env = Object.assign(process.env, loadEnv(mode, process.cwd(), ""));

  return defineConfig({
    define: {
      "import.meta.env.VITE_VERSION_JS": version.toString(),
    },

    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },

    plugins: [
      react(),
      tailwindcss(),
    ],

    build: {
      cssCodeSplit: true,
      chunkSizeWarningLimit: 3000,
      rollupOptions: {
        input: {
          main: resolve(__dirname, "index.html"),
        },
        output: {
          assetFileNames: (asset) => {
            return "assets/[name].[hash][extname]";
          },
        },
      },
    },
    
    base: process.env.VITE_BASE,
  })
}