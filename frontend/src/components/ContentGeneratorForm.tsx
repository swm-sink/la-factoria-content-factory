import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { JobMetadata, ApiError, ContentType } from '../types/content';
import api from '../api'; // Assuming api.ts is configured for axios instance

const availableContentTypes: { id: ContentType; label: string }[] = [
  { id: 'content_outline', label: 'Content Outline' },
  { id: 'podcast_script', label: 'Podcast Script' },
  { id: 'study_guide', label: 'Study Guide' },
  { id: 'one_pager_summary', label: 'One-Pager Summary' },
  { id: 'detailed_reading_material', label: 'Detailed Reading Material' },
  { id: 'faqs', label: 'FAQs' },
  { id: 'flashcards', label: 'Flashcards' },
  { id: 'reading_guide_questions', label: 'Reading Guide Questions' },
];

export const ContentGeneratorForm: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [formData, setFormData] = useState<JobMetadata & { target_pages?: number; use_parallel?: boolean; use_cache?: boolean; }>({
    syllabus_text: '',
    requested_content_types: ['content_outline'],
    target_audience: '',
    difficulty: 'intermediate',
    length: 'medium',
    target_duration_minutes: 10,
    target_pages: 1,
    generate_audio: false,
    use_parallel: true,
    use_cache: true,
  });

  const handleCheckboxChange = (contentType: ContentType) => {
    setFormData((prev) => {
      const newContentTypes = prev.requested_content_types.includes(contentType)
        ? prev.requested_content_types.filter((ct) => ct !== contentType)
        : [...prev.requested_content_types, contentType];
      return { ...prev, requested_content_types: newContentTypes };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setJobId(null);

    if (formData.requested_content_types.length === 0) {
      setError('Please select at least one content type.');
      setIsLoading(false);
      return;
    }

    // Construct payload matching backend ContentRequest (flattened)
    // JobCreationRequest is already flat. formData (JobMetadata) has extra fields.
    const requestPayload = {
      syllabus_text: formData.syllabus_text,
      target_format: formData.requested_content_types[0] || "comprehensive", // Use first selected or comprehensive
      target_duration: formData.target_duration_minutes || undefined,
      target_pages: formData.target_pages || undefined,
      use_parallel: formData.use_parallel !== undefined ? formData.use_parallel : true, // Default to true if not set
      use_cache: formData.use_cache !== undefined ? formData.use_cache : true,       // Default to true if not set
    };

    try {
      // Ensure your api.ts is configured to handle requests to your backend
      // The backend endpoint is /api/v1/jobs
      const response = await api.post('/api/v1/jobs', requestPayload);
      setJobId(response.data.id);
      // Navigate to a job status page, or display status inline
      // For now, just log and prepare for FE-3.3
      console.log('Job created successfully:', response.data);
      navigate(`/jobs/${response.data.id}`); // Example navigation
    } catch (err) {
      const apiError = err as ApiError; // Or AxiosError
      setError(apiError.message || 'Failed to create content generation job. Please try again.');
      console.error('Job creation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      const { checked } = e.target as HTMLInputElement;
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: value ? parseInt(value, 10) : undefined }));
    }
    else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-3xl mx-auto p-8 bg-white shadow-lg rounded-lg">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Create New Content Generation Job</h2>

      <div>
        <label htmlFor="syllabus_text" className="block text-sm font-medium text-gray-700 mb-1">
          Syllabus / Topic Description
        </label>
        <textarea
          id="syllabus_text"
          name="syllabus_text"
          rows={4}
          value={formData.syllabus_text}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
          placeholder="Enter the detailed syllabus, topic, or text to generate content from (min 50 chars)"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Requested Content Types
        </label>
        <div className="mt-2 grid grid-cols-2 gap-4 sm:grid-cols-3">
          {availableContentTypes.map((contentType) => (
            <div key={contentType.id} className="flex items-center">
              <input
                id={contentType.id}
                name={contentType.id}
                type="checkbox"
                checked={formData.requested_content_types.includes(contentType.id)}
                onChange={() => handleCheckboxChange(contentType.id)}
                className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <label htmlFor={contentType.id} className="ml-2 block text-sm text-gray-900">
                {contentType.label}
              </label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <label htmlFor="targetAudience" className="block text-sm font-medium text-gray-700 mb-1">
          Target Audience (Optional)
        </label>
        <input
          type="text"
          id="targetAudience"
          name="target_audience"
          value={formData.target_audience ?? ''}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
          placeholder="e.g., High school students, Professionals"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label htmlFor="target_duration_minutes" className="block text-sm font-medium text-gray-700 mb-1">
            Target Duration (minutes, for Podcast - Optional)
          </label>
          <input
            type="number"
            id="target_duration_minutes"
            name="target_duration_minutes"
            value={formData.target_duration_minutes || ''}
            onChange={handleChange}
            min="1"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            placeholder="e.g., 10"
          />
        </div>
        <div>
          <label htmlFor="target_pages" className="block text-sm font-medium text-gray-700 mb-1">
            Target Pages (for Documents - Optional)
          </label>
          <input
            type="number"
            id="target_pages"
            name="target_pages"
            value={formData.target_pages || ''}
            onChange={handleChange}
            min="1"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            placeholder="e.g., 5"
          />
        </div>
        <div>
          <label htmlFor="difficulty" className="block text-sm font-medium text-gray-700 mb-1">
            Difficulty Level (Optional)
          </label>
          <select
            id="difficulty"
            name="difficulty"
            value={formData.difficulty}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
      </div>

      <div className="flex items-center">
        <input
          id="generate_audio"
          name="generate_audio"
          type="checkbox"
          checked={formData.generate_audio ?? false}
          onChange={handleChange}
          className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
        />
        <label htmlFor="generate_audio" className="ml-2 block text-sm text-gray-900">
          Generate Audio for Podcast Script (Optional)
        </label>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
         <div>
          <label htmlFor="use_parallel" className="flex items-center">
            <input
              id="use_parallel"
              name="use_parallel"
              type="checkbox"
              checked={formData.use_parallel ?? true}
              onChange={handleChange}
              className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-900">Use Parallel Processing</span>
          </label>
        </div>
        <div>
          <label htmlFor="use_cache" className="flex items-center">
            <input
              id="use_cache"
              name="use_cache"
              type="checkbox"
              checked={formData.use_cache ?? true}
              onChange={handleChange}
              className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-900">Use Cache</span>
          </label>
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4 mt-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      {jobId && (
        <div className="rounded-md bg-green-50 p-4 mt-4">
          <div className="text-sm text-green-700">
            Job created successfully! Job ID: {jobId}. You will be redirected or can view status soon.
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading || formData.requested_content_types.length === 0}
        className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed transition-opacity"
      >
        {isLoading ? 'Creating Job...' : 'Create Content Generation Job'}
      </button>
    </form>
  );
};
