import React from 'react';
import { useError } from '../../contexts/ErrorContext';

const ErrorDisplay: React.FC = () => {
  const { error, clearError } = useError();

  if (!error) {
    return null;
  }

  return (
    <div
      className="fixed bottom-4 right-4 z-50 p-4 max-w-sm w-full bg-red-100 border border-red-400 text-red-700 rounded-md shadow-lg"
      role="alert"
    >
      <div className="flex">
        <div className="py-1">
          {/* Heroicon: x-circle */}
          <svg className="fill-current h-6 w-6 text-red-500 mr-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" />
          </svg>
        </div>
        <div>
          <p className="font-bold">Error</p>
          <p className="text-sm">{error}</p>
        </div>
        <div className="ml-auto pl-3">
          <button
            onClick={clearError}
            className="-mx-1.5 -my-1.5 bg-red-100 text-red-500 rounded-lg focus:ring-2 focus:ring-red-400 p-1.5 hover:bg-red-200 inline-flex h-8 w-8"
            aria-label="Dismiss"
          >
            <span className="sr-only">Dismiss</span>
            {/* Heroicon: x */}
            <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ErrorDisplay;
