import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/rules": "http://localhost:8000",
      "/matching": "http://localhost:8000",
      "/exceptions": "http://localhost:8000",
      "/reporting": "http://localhost:8000",
      "/billing": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
});
