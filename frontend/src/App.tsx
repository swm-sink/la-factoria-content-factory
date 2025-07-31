import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import { lazyLoad } from './utils/lazy';

// Lazy load all route components for code splitting
const Navbar = lazy(() => import('./components/Layout/Navbar'));
const ErrorDisplay = lazy(() => import('./components/common/ErrorDisplay'));
const HomePage = lazy(() => import('./pages/HomePage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const GeneratePage = lazy(() => import('./pages/GeneratePage'));
const JobStatusPage = lazy(() => import('./pages/JobStatusPage'));

// Lazy load admin components (larger bundle)
const UsageDashboard = lazyLoad(
  () => import('./pages/Admin/UsageDashboard'),
  <div className="flex justify-center items-center h-64">
    <LoadingSpinner />
    <span className="ml-2">Loading admin dashboard...</span>
  </div>
);

const SLADashboard = lazyLoad(
  () => import('./pages/Admin/SLADashboard'),
  <div className="flex justify-center items-center h-64">
    <LoadingSpinner />
    <span className="ml-2">Loading SLA dashboard...</span>
  </div>
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Optimize refetching
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (renamed from cacheTime)
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Loading fallback component
const PageLoader = () => (
  <div className="flex justify-center items-center min-h-[50vh]">
    <LoadingSpinner />
  </div>
);

export const App = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <div className="min-h-screen bg-gray-50 flex flex-col">
          <Suspense fallback={<div className="h-16 bg-white border-b" />}>
            <Navbar />
          </Suspense>
          
          <Suspense fallback={null}>
            <ErrorDisplay />
          </Suspense>
          
          <main className="flex-grow">
            <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
              <Suspense fallback={<PageLoader />}>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/generate" element={<GeneratePage />} />
                  <Route path="/jobs/:jobId" element={<JobStatusPage />} />
                  <Route path="/admin/usage" element={<UsageDashboard />} />
                  <Route path="/admin/sla" element={<SLADashboard />} />
                </Routes>
              </Suspense>
            </div>
          </main>
          
          <footer className="bg-white border-t">
            <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-500">
              &copy; {new Date().getFullYear()} AI Content Factory. All rights reserved.
            </div>
          </footer>
        </div>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;