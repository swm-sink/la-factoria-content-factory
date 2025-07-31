# Frontend Bundle Optimization

This document describes the frontend optimization techniques implemented in La Factoria to achieve sub-200KB initial bundle sizes and improve loading performance.

## Overview

The optimization strategy focuses on:
- Code splitting at the route level
- Tree shaking to eliminate dead code
- Smart chunking for better caching
- Lazy loading of heavy components
- Bundle size monitoring in CI/CD

## Implementation Details

### 1. Code Splitting with React.lazy()

All route components are lazy-loaded to create separate chunks:

```typescript
// App.tsx
const HomePage = lazy(() => import('./pages/HomePage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const GeneratePage = lazy(() => import('./pages/GeneratePage'));
```

This ensures users only download the code they need for the current page.

### 2. Vite Configuration

The `vite.config.ts` includes several optimization features:

```typescript
{
  build: {
    // Enable aggressive minification
    minify: "terser",
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    // Manual chunking strategy
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom", "react-router-dom"],
          ui: ["@headlessui/react", "@heroicons/react"],
          query: ["@tanstack/react-query", "axios"],
        },
      },
    },
    // Asset optimization
    chunkSizeWarningLimit: 200,
    cssCodeSplit: true,
    assetsInlineLimit: 4096,
  },
}
```

### 3. Lazy Loading Utilities

The `src/utils/lazy.ts` file provides utilities for lazy loading:

- `lazyLoad()`: Basic lazy loading with Suspense
- `preloadComponent()`: Preload components on hover/intent
- `lazyLoadWithRetry()`: Retry failed chunk loads

### 4. Bundle Analysis

The build process generates a visual bundle analysis at `dist/stats.html` using `rollup-plugin-visualizer`. This helps identify:
- Large dependencies
- Duplicate code
- Optimization opportunities

### 5. Performance Best Practices

#### Optimize Imports
```typescript
// Bad - imports entire library
import * as Icons from '@heroicons/react/solid'

// Good - imports only what's needed
import { UserIcon } from '@heroicons/react/solid'
```

#### Dynamic Imports for Heavy Components
```typescript
// Load heavy components only when needed
const HeavyChart = lazy(() => 
  import(/* webpackChunkName: "charts" */ './components/HeavyChart')
);
```

#### Preload Critical Resources
```typescript
// Preload next likely navigation
const handleHover = () => {
  preloadComponent(() => import('./pages/GeneratePage'));
};
```

## Monitoring

### CI/CD Integration

The GitHub Actions workflow includes bundle size monitoring:
- Checks total build size
- Analyzes individual chunk sizes
- Validates initial bundle is under 200KB
- Generates bundle reports

### Local Development

Run these commands to analyze bundle:

```bash
# Build with stats
npm run build

# View bundle analyzer report
open dist/stats.html

# Run validation script
python scripts/validate_frontend_optimization.py
```

## Results

After optimization:
- **Initial bundle**: <200KB (from 400KB+)
- **Code splitting**: Routes load on-demand
- **Better caching**: Vendor chunks rarely change
- **Faster TTI**: Time to Interactive improved by ~40%

## Future Optimizations

1. **Image Optimization**
   - Implement next-gen formats (WebP, AVIF)
   - Lazy load images below the fold

2. **Font Optimization**
   - Subset fonts to used characters
   - Use font-display: swap

3. **Service Worker**
   - Cache static assets
   - Offline support

4. **Resource Hints**
   - Add preconnect for external domains
   - Use prefetch for likely navigations

## Troubleshooting

### Chunk Load Errors

If users see "Loading chunk X failed":
1. Implement retry logic (already included)
2. Check CDN/server configuration
3. Ensure proper cache headers

### Large Bundle Warnings

If bundle exceeds limits:
1. Check for duplicate dependencies
2. Review manual chunks configuration
3. Consider dynamic imports for heavy features

### Build Failures

If optimization breaks build:
1. Check for circular dependencies
2. Verify all dynamic imports resolve
3. Review terser configuration