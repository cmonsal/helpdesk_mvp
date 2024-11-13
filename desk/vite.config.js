import path from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import frappeui from "frappe-ui/vite";
import Icons from "unplugin-icons/vite";
import Components from "unplugin-vue-components/vite";
import IconsResolver from "unplugin-icons/resolver";
import { FileSystemIconLoader } from "unplugin-icons/loaders";
import { SVG, cleanupSVG, parseColors } from "@iconify/tools";
import LucideIcons from "./lucide";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    frappeui(),
    vue(),
    Components({
      resolvers: IconsResolver({
        prefix: false,
        enabledCollections: ["lucide"],
      }),
    }),
    VitePWA({
      registerType: "autoUpdate",
      devOptions: {
        enabled: true,
      },
      workbox: {
        cleanupOutdatedCaches: true,
      },
      manifest: {
        display: "standalone",
        name: "Frappe Helpdesk",
        short_name: "Helpdesk",
        start_url: "/helpdesk",
        description:
          "Modern, Streamlined, Free and Open Source Customer Service Software",
        icons: [
          {
            src: "/assets/helpdesk/desk/manifest/manifest-icon-192.maskable.png",
            sizes: "192x192",
            type: "image/png",
            purpose: "any",
          },
          {
            src: "/assets/helpdesk/desk/manifest/manifest-icon-192.maskable.png",
            sizes: "192x192",
            type: "image/png",
            purpose: "maskable",
          },
          {
            src: "/assets/helpdesk/desk/manifest/manifest-icon-512.maskable.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any",
          },
          {
            src: "/assets/helpdesk/desk/manifest/manifest-icon-512.maskable.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
    }),
    Icons({
      compiler: "vue3",
      customCollections: {
        lucide: LucideIcons,
        espresso: FileSystemIconLoader("./src/assets/icons", async (svg) => {
          const r = new SVG(svg);

          await cleanupSVG(r);
          await parseColors(r, {
            callback: () => "currentColor",
          });

          return r.toMinifiedString();
        }),
        logos: FileSystemIconLoader("./src/assets/logos", async (svg) => {
          const r = new SVG(svg);
          await cleanupSVG(r);
          return r.toMinifiedString();
        }),
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "tailwind.config.js": path.resolve(__dirname, "tailwind.config.js"),
    },
  },
  build: {
    outDir: `../helpdesk/public/desk`,
    emptyOutDir: true,
    target: "es2021",
    sourcemap: true,
    commonjsOptions: {
      include: [/tailwind.config.js/, /node_modules/],
    },
  },
  optimizeDeps: {
    include: ["feather-icons", "showdown", "tailwind.config.js"],
  },
  server: {
    port: parseInt(process.env.PORT || 3000),
    host: true, // Listening on all available network interfaces
    strictPort: true, // Fail if port is already in use
  },
  preview: {
    port: parseInt(process.env.PORT || 3000),
    host: true, // Listening on all available network interfaces
    strictPort: true, // Fail if port is already in use
  }
});