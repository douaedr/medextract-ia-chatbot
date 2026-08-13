import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // En dev local, proxy vers l'API Gateway (DEV 1)
    proxy: {
      "/api": { target: "http://localhost:8080", changeOrigin: true },
    },
  },
});
