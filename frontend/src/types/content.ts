export interface ContentGenerationRequest {
  topic: string;
  contentType: 'study_guide' | 'podcast_script' | 'summary' | 'detailed_reading';
  targetAudience: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  length: 'short' | 'medium' | 'long';
}

export interface ContentGenerationResponse {
  id: string;
  topic: string;
  contentType: string;
  content: {
    outline: string;
    mainContent: string;
    summary?: string;
    keyPoints?: string[];
    questions?: string[];
    audioUrl?: string;
  };
  metadata: {
    createdAt: string;
    tokenCount: number;
    processingTime: number;
  };
}

export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, unknown>;
} 