import React from 'react';
import { useParams } from 'react-router-dom';
import JobStatusDisplay from '../components/Job/JobStatusDisplay';

const JobStatusPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();

  return (
    <div className="py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Job Status</h1>
        {jobId ? (
          <p className="mt-1 text-sm text-gray-600">
            Tracking status for Job ID: {jobId}
          </p>
        ) : (
          <p className="mt-1 text-sm text-red-600">
            No Job ID provided in the URL.
          </p>
        )}
      </header>
      
      {jobId ? (
        <JobStatusDisplay jobId={jobId} />
      ) : (
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <p className="text-gray-700">Please provide a Job ID in the URL to see its status (e.g., /jobs/your-job-id).</p>
        </div>
      )}
    </div>
  );
};

export default JobStatusPage;
