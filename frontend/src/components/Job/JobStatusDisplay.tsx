import React, { useEffect, useState } from 'react';
import api from '../../api';
import { JobStatusPollResponse, ApiError } from '../../types/content'; // Assuming JobResponse is defined

interface JobStatusDisplayProps {
  jobId: string;
}

const JobStatusDisplay: React.FC<JobStatusDisplayProps> = ({ jobId }) => {
  const [job, setJob] = useState<JobStatusPollResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!jobId) return;

    const fetchJobStatus = async () => {
      setIsLoading(true);
      setError(null);
      try {
        console.log(`Fetching status for job ID: ${jobId}`);
        const response = await api.get(`/api/v1/jobs/${jobId}`);
        setJob(response.data);
      } catch (err) {
        const apiError = err as ApiError; // Or AxiosError if you have specific Axios error handling
        setError(apiError.message || 'Failed to fetch job status.');
        console.error('Error fetching job status:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchJobStatus();

    // Basic polling example (can be improved with react-query or other libraries)
    const intervalId = setInterval(() => {
      if (job && (job.status === 'pending' || job.status === 'processing')) {
        fetchJobStatus();
      }
    }, 5000); // Poll every 5 seconds if job is still active

    return () => clearInterval(intervalId);
  }, [jobId, job]); // Add job to dependency array to re-evaluate polling

  if (!jobId) {
    return <p className="text-center text-gray-500">No job selected.</p>;
  }

  if (isLoading) {
    return <p className="text-center text-blue-500">Loading job status for {jobId}...</p>;
  }

  if (error) {
    return <p className="text-center text-red-500">Error: {error}</p>;
  }

  if (!job) {
    return <p className="text-center text-gray-500">Job data not found.</p>;
  }

  return (
    <div className="mt-8 bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">Job Status: {job.id}</h3>
      <div className="space-y-2">
        <p><span className="font-medium">Status:</span> <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
          job.status === 'completed' ? 'bg-green-100 text-green-800' :
          job.status === 'failed' ? 'bg-red-100 text-red-800' :
          job.status === 'processing' ? 'bg-blue-100 text-blue-800' :
          'bg-yellow-100 text-yellow-800'
        }`}>{job.status}</span></p>
        <p><span className="font-medium">Created:</span> {new Date(job.created_at).toLocaleString()}</p>
        <p><span className="font-medium">Last Updated:</span> {new Date(job.updated_at).toLocaleString()}</p>
        
        {job.progress && (
          <div>
            <p className="font-medium">Progress:</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 my-1">
              <div 
                className="bg-blue-600 h-2.5 rounded-full" 
                style={{ width: `${job.progress.percentage || 0}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600">{job.progress.current_step} ({job.progress.completed_steps}/{job.progress.total_steps} steps - {job.progress.percentage || 0}%)</p>
          </div>
        )}

        {job.status === 'completed' && job.result && (
          <div className="mt-4">
            <h4 className="text-lg font-semibold text-gray-700">Results:</h4>
            <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto text-sm">
              {JSON.stringify(job.result, null, 2)}
            </pre>
          </div>
        )}
        {job.status === 'failed' && job.error && (
          <p className="text-red-600"><span className="font-medium">Error Details:</span> {job.error.message} (Code: {job.error.code})</p>
        )}
      </div>
    </div>
  );
};

export default JobStatusDisplay;
