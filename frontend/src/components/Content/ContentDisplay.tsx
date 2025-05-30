import React, { useState } from 'react';
import { GeneratedContent, ApiError } from '../../types/content'; // Assuming GeneratedContent is defined
import api from '../../api'; // Assuming api.ts is configured

interface ContentDisplayProps {
  contentId: string; // This would be the ID of the specific content piece, or job ID if feedback is per-job
  generatedContent: GeneratedContent | null | undefined;
}

const ContentDisplay: React.FC<ContentDisplayProps> = ({ contentId, generatedContent }) => {
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<{ type: 'like' | 'dislike'; message: string } | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);

  const handleFeedback = async (liked: boolean) => {
    setFeedbackError(null);
    setFeedbackSubmitted(null);
    console.log(`Feedback for ${contentId}: ${liked ? 'Like' : 'Dislike'}`);
    
    try {
      // Assuming contentId is the ID the backend /api/v1/content/{content_id}/feedback expects.
      // This might be a specific ID of a content piece within the job, or the job ID itself
      // if feedback is at the job level. This needs to align with backend API design.
      await api.post(`/v1/feedback/content/${contentId}/feedback`, { 
        rating: liked,
        // comment: "Optional comment here" // Add if comment field is implemented
      });

      setFeedbackSubmitted({ 
        type: liked ? 'like' : 'dislike', 
        message: `Thank you for your feedback! You ${liked ? 'liked' : 'disliked'} this content.` 
      });
    } catch (err) {
      const apiError = err as ApiError; // Or AxiosError
      setFeedbackError(apiError.message || 'Failed to submit feedback.');
      console.error('Feedback submission error:', err);
    }
  };

  if (!generatedContent) {
    return <p className="text-gray-500">No content to display.</p>;
  }

  return (
    <div className="mt-6 bg-white p-6 rounded-lg shadow">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">Generated Content</h3>
      
      {/* Placeholder for actual content rendering */}
      <div className="prose max-w-none">
        <p className="text-gray-700 mb-2"><strong>Content Outline:</strong></p>
        <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
          {JSON.stringify(generatedContent.content_outline || { message: "Outline not generated or available." }, null, 2)}
        </pre>

        {generatedContent.podcast_script && (
          <>
            <p className="text-gray-700 mt-4 mb-2"><strong>Podcast Script:</strong></p>
            <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
              {JSON.stringify(generatedContent.podcast_script, null, 2)}
            </pre>
          </>
        )}
        {/* Add rendering for other content types as needed */}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <h4 className="text-md font-semibold text-gray-700 mb-2">Rate this content:</h4>
        <div className="flex space-x-3">
          <button
            onClick={() => handleFeedback(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            aria-label="Like this content"
          >
            {/* Heroicon: thumb-up (outline) */}
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
            </svg>
            Like
          </button>
          <button
            onClick={() => handleFeedback(false)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            aria-label="Dislike this content"
          >
            {/* Heroicon: thumb-down (outline) */}
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.737 3h4.017c.163 0 .326.02.485.06L17 4m-7 10v5a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 13V4m-7 10h2m-2 0H5a2 2 0 00-2 2v6a2 2 0 002 2h2.5" />
            </svg>
            Dislike
          </button>
        </div>
        {feedbackSubmitted && (
          <p className={`mt-3 text-sm ${feedbackSubmitted.type === 'like' ? 'text-green-600' : 'text-red-600'}`}>
            {feedbackSubmitted.message}
          </p>
        )}
        {feedbackError && <p className="mt-3 text-sm text-red-600">{feedbackError}</p>}
      </div>
    </div>
  );
};

export default ContentDisplay;
