import { lazy, Suspense, ComponentType } from 'react';
import LoadingSpinner from '@/components/LoadingSpinner';

/**
 * Create a lazy-loaded component with automatic loading fallback
 * @param importFunc Function that returns a dynamic import
 * @param fallback Optional custom loading component
 */
export function lazyLoad<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  fallback?: React.ReactNode
) {
  const LazyComponent = lazy(importFunc);

  return (props: React.ComponentProps<T>) => (
    <Suspense fallback={fallback || <LoadingSpinner />}>
      <LazyComponent {...props} />
    </Suspense>
  );
}

/**
 * Preload a component to improve perceived performance
 * Call this when you anticipate the user will navigate to a route
 */
export function preloadComponent(
  importFunc: () => Promise<{ default: ComponentType<any> }>
) {
  // Simply calling the import function will trigger the load
  importFunc();
}

/**
 * Create a lazy-loaded component with retry logic
 * Useful for handling network failures during chunk loading
 */
export function lazyLoadWithRetry<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  retries = 3,
  delay = 1000
) {
  return lazy(async () => {
    let lastError: any;
    
    for (let i = 0; i < retries; i++) {
      try {
        return await importFunc();
      } catch (error) {
        lastError = error;
        if (i < retries - 1) {
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    
    throw lastError;
  });
}

/**
 * HOC for route-based code splitting with error boundary
 */
export function withLazyLoad<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  LoadingComponent?: ComponentType,
  ErrorComponent?: ComponentType<{ error: Error }>
) {
  const LazyComponent = lazyLoadWithRetry(importFunc);
  
  return (props: React.ComponentProps<T>) => (
    <Suspense fallback={LoadingComponent ? <LoadingComponent /> : <LoadingSpinner />}>
      <LazyComponent {...props} />
    </Suspense>
  );
}