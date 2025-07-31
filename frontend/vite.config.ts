import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [
    react(),
    // Bundle analyzer will be added after fixing the build
  ],
  resolve: {
    alias: { 
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    // Enable minification
    minify: "terser",
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    // Optimize chunk size
    target: "es2015",
    // Manual chunks for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunk for React and core dependencies
          vendor: ["react", "react-dom", "react-router-dom"],
          // UI components chunk
          ui: ["@headlessui/react", "@heroicons/react"],
          // Data fetching chunk
          query: ["@tanstack/react-query", "axios"],
        },
        // Optimize chunk names
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : 'chunk';
          return `assets/js/${facadeModuleId}-[hash].js`;
        },
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    // Set chunk size warnings
    chunkSizeWarningLimit: 200, // 200KB warning threshold
    // Enable source maps for production debugging
    sourcemap: true,
    // CSS code splitting
    cssCodeSplit: true,
    // Asset inlining threshold
    assetsInlineLimit: 4096, // 4KB
    // Generate bundle stats
    reportCompressedSize: true,
  },
  optimizeDeps: {
    // Pre-bundle these dependencies
    include: ["react", "react-dom", "react-router-dom"],
    // Exclude large libraries from pre-bundling if needed
    exclude: [],
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});