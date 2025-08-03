/**
 * Content Generation Form Component for La Factoria
 * ================================================
 *
 * This example demonstrates the recommended React pattern for content generation forms.
 * Follows the "simple implementation" principle while maintaining good UX and type safety.
 *
 * Key patterns demonstrated:
 * - TypeScript for type safety
 * - Form validation and error handling
 * - API integration with proper loading states
 * - Educational content type selection
 * - Responsive design considerations
 */

import React, { useState, useEffect } from 'react';

// Types for La Factoria content generation
interface ContentRequest {
  topic: string;
  content_type: string;
  target_audience: string;
  language: string;
}

interface ContentResponse {
  id: string;
  topic: string;
  content_type: string;
  content: string;
  quality_score: number;
  created_at: string;
}

interface FormErrors {
  topic?: string;
  content_type?: string;
  target_audience?: string;
}

// Content types matching backend API
const CONTENT_TYPES = [
  { value: 'master_content_outline', label: 'Master Content Outline', description: 'Foundation structure with learning objectives' },
  { value: 'podcast_script', label: 'Podcast Script', description: 'Conversational audio content with speaker notes' },
  { value: 'study_guide', label: 'Study Guide', description: 'Comprehensive educational material with key concepts' },
  { value: 'one_pager_summary', label: 'One-Pager Summary', description: 'Concise overview with essential takeaways' },
  { value: 'detailed_reading_material', label: 'Detailed Reading Material', description: 'In-depth content with examples and exercises' },
  { value: 'faq_collection', label: 'FAQ Collection', description: 'Question-answer pairs covering common topics' },
  { value: 'flashcards', label: 'Flashcards', description: 'Term-definition pairs for memorization and review' },
  { value: 'reading_guide_questions', label: 'Reading Guide Questions', description: 'Discussion questions for comprehension' },
];

// Target audience options
const TARGET_AUDIENCES = [
  { value: 'elementary', label: 'Elementary School' },
  { value: 'middle-school', label: 'Middle School' },
  { value: 'high-school', label: 'High School' },
  { value: 'college', label: 'College' },
  { value: 'adult-learning', label: 'Adult Learning' },
];

const ContentGenerationForm: React.FC = () => {
  // Form state
  const [formData, setFormData] = useState<ContentRequest>({
    topic: '',
    content_type: '',
    target_audience: 'high-school',
    language: 'en'
  });

  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [generatedContent, setGeneratedContent] = useState<ContentResponse | null>(null);
  const [apiKey, setApiKey] = useState<string>('');

  // Load API key from localStorage on component mount
  useEffect(() => {
    const savedApiKey = localStorage.getItem('la-factoria-api-key');
    if (savedApiKey) {
      setApiKey(savedApiKey);
    }
  }, []);

  // Form validation
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.topic.trim()) {
      newErrors.topic = 'Topic is required';
    } else if (formData.topic.length < 3) {
      newErrors.topic = 'Topic must be at least 3 characters long';
    }

    if (!formData.content_type) {
      newErrors.content_type = 'Content type is required';
    }

    if (!formData.target_audience) {
      newErrors.target_audience = 'Target audience is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    if (!apiKey) {
      alert('Please set your API key first');
      return;
    }

    setIsLoading(true);
    setGeneratedContent(null);

    try {
      const response = await fetch('/api/v1/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Content generation failed');
      }

      const result: ContentResponse = await response.json();
      setGeneratedContent(result);

      // Clear form after successful generation
      setFormData({
        topic: '',
        content_type: '',
        target_audience: 'high-school',
        language: 'en'
      });

    } catch (error) {
      console.error('Generation error:', error);
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle input changes
  const handleInputChange = (field: keyof ContentRequest) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));

    // Clear errors when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  // Save API key
  const handleApiKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newApiKey = e.target.value;
    setApiKey(newApiKey);
    localStorage.setItem('la-factoria-api-key', newApiKey);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        La Factoria Content Generator
      </h1>

      {/* API Key Input */}
      <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
        <label htmlFor="api-key" className="block text-sm font-medium text-gray-700 mb-2">
          API Key (stored locally)
        </label>
        <input
          id="api-key"
          type="password"
          value={apiKey}
          onChange={handleApiKeyChange}
          placeholder="Enter your API key"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Topic Input */}
        <div>
          <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-2">
            Educational Topic *
          </label>
          <input
            id="topic"
            type="text"
            value={formData.topic}
            onChange={handleInputChange('topic')}
            placeholder="e.g., Python Programming Basics, World War II, Algebra Fundamentals"
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.topic ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.topic && (
            <p className="mt-1 text-sm text-red-600">{errors.topic}</p>
          )}
        </div>

        {/* Content Type Selection */}
        <div>
          <label htmlFor="content-type" className="block text-sm font-medium text-gray-700 mb-2">
            Content Type *
          </label>
          <select
            id="content-type"
            value={formData.content_type}
            onChange={handleInputChange('content_type')}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.content_type ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">Select content type...</option>
            {CONTENT_TYPES.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          {formData.content_type && (
            <p className="mt-1 text-sm text-gray-600">
              {CONTENT_TYPES.find(t => t.value === formData.content_type)?.description}
            </p>
          )}
          {errors.content_type && (
            <p className="mt-1 text-sm text-red-600">{errors.content_type}</p>
          )}
        </div>

        {/* Target Audience */}
        <div>
          <label htmlFor="target-audience" className="block text-sm font-medium text-gray-700 mb-2">
            Target Audience *
          </label>
          <select
            id="target-audience"
            value={formData.target_audience}
            onChange={handleInputChange('target_audience')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {TARGET_AUDIENCES.map(audience => (
              <option key={audience.value} value={audience.value}>
                {audience.label}
              </option>
            ))}
          </select>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-3 px-4 rounded-md text-white font-medium ${
            isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
          } transition duration-200`}
        >
          {isLoading ? 'Generating Content...' : 'Generate Educational Content'}
        </button>
      </form>

      {/* Generated Content Display */}
      {generatedContent && (
        <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-md">
          <h2 className="text-xl font-semibold text-green-800 mb-4">
            Generated Content
          </h2>
          <div className="space-y-3">
            <p><strong>Topic:</strong> {generatedContent.topic}</p>
            <p><strong>Type:</strong> {generatedContent.content_type}</p>
            <p><strong>Quality Score:</strong> {(generatedContent.quality_score * 100).toFixed(1)}%</p>
            <div className="mt-4">
              <h3 className="font-medium text-gray-700 mb-2">Content:</h3>
              <div className="bg-white p-4 border rounded-md max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm">
                  {generatedContent.content}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentGenerationForm;

/**
 * Usage Example:
 *
 * import ContentGenerationForm from './components/ContentGenerationForm';
 *
 * function App() {
 *   return (
 *     <div className="App">
 *       <ContentGenerationForm />
 *     </div>
 *   );
 * }
 *
 * This component demonstrates:
 * - Complete form handling for educational content generation
 * - Type-safe TypeScript patterns
 * - Error handling and validation
 * - API integration following La Factoria backend patterns
 * - Responsive design with Tailwind CSS
 * - Local storage for API key management
 * - Loading states and user feedback
 */
