import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ErrorBoundary } from './components/ErrorBoundary'
import { ContentGeneratorForm } from './components/ContentGeneratorForm'

const queryClient = new QueryClient()

export const App = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow">
              <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold text-gray-900">AI Content Factory</h1>
              </div>
            </header>
            <main>
              <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <Routes>
                  <Route path="/" element={<ContentGeneratorForm />} />
                  <Route path="/generate" element={<ContentGenerator />} />
                  <Route path="/history" element={<History />} />
                </Routes>
              </div>
            </main>
          </div>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App 