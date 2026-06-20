import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "CommunityHealth",
        short_name: "ComHealth",
        description: "Community-driven public health dashboard and alerts",
        theme_color: "#1a6b54",
        display: "standalone",
        icons: [],
      },
      workbox: {
        // Cache the shell + allow queued background sync for offline
        // symptom/mood logging so it works on low-connectivity networks.
        runtimeCaching: [
          {
            urlPattern: /\/api\//,
            handler: "NetworkFirst",
          },
        ],
      },
    }),
  ],
  server: { port: 5173 },
});
