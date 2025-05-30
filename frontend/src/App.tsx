import { Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'; // Updated import
import { ErrorBoundary } from './components/ErrorBoundary';
import Navbar from './components/Layout/Navbar';
import ErrorDisplay from './components/common/ErrorDisplay'; // Import ErrorDisplay
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import GeneratePage from './pages/GeneratePage'; // Ensuring this path is correct
import JobStatusPage from './pages/JobStatusPage';
// import { ContentGeneratorForm } from './components/ContentGeneratorForm';
// import ContentGenerator from './pages/ContentGenerator';
// import History from './pages/History'; // To be added later if needed

const queryClient = new QueryClient();

// Placeholder for HomePage
// const HomePage = () => (
//   <div className="text-center">
//     <h2 className="text-2xl font-semibold mt-10">Welcome to the AI Content Factory!</h2>
//     <p className="mt-4">Please login or register to start generating content.</p>
//   </div>
// );

// Placeholder for GeneratePage
// const GeneratePage = () => (
//   <div className="text-center">
//     <h2 className="text-2xl font-semibold mt-10">Generate Content</h2>
//     <p className="mt-4">Content generation form will be here.</p>
//     {/* <ContentGeneratorForm /> */} {/* Or the actual content generation component */}
//   </div>
// );


export const App = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        {/* BrowserRouter is now in main.tsx */}
        <div className="min-h-screen bg-gray-50 flex flex-col">
          <Navbar />
          <ErrorDisplay /> {/* Add ErrorDisplay globally */}
          <main className="flex-grow">
            <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/generate" element={<GeneratePage />} />
                <Route path="/jobs/:jobId" element={<JobStatusPage />} /> {/* Add route for JobStatusPage */}
                {/* <Route path="/history" element={<History />} /> */}
              </Routes>
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
