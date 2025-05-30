import React from 'react';
import RegistrationForm from '../components/Auth/RegistrationForm';
// import { Navigate } from 'react-router-dom';
// import { useAuth } from '../contexts/AuthContext';

const RegisterPage: React.FC = () => {
  // const { isAuthenticated } = useAuth();

  // if (isAuthenticated) {
  //   return <Navigate to="/dashboard" replace />; // Or wherever authenticated users should go
  // }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Placeholder for a logo or app name if desired */}
        {/* <img className="mx-auto h-12 w-auto" src="/logo.svg" alt="Workflow" /> */}
        <h1 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h1>
      </div>
      <RegistrationForm />
    </div>
  );
};

export default RegisterPage;
