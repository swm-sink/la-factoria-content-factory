export type ContentType =
  | 'content_outline'
  | 'podcast_script'
  | 'study_guide'
  | 'one_pager_summary'
  | 'detailed_reading_material'
  | 'faqs'
  | 'flashcards'
  | 'reading_guide_questions';

// --- Specific Content Type Interfaces (matching Pydantic models) ---

export interface OutlineSection {
  section_number: number;
  title: string;
  description: string;
  estimated_duration_minutes?: number | null;
  key_points: string[];
}

export interface ContentOutline {
  title: string;
  overview: string;
  learning_objectives: string[];
  sections: OutlineSection[];
  estimated_total_duration?: number | null;
  target_audience?: string | null;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced' | string; // Pydantic has default, so it's always present
}

export interface PodcastScript {
  title: string;
  introduction: string;
  main_content: string;
  conclusion: string;
  speaker_notes?: string[] | null;
  estimated_duration_minutes?: number | null;
}

export interface StudyGuide {
  title: string;
  overview: string;
  key_concepts: string[];
  detailed_content: string;
  summary: string;
  recommended_reading?: string[] | null;
}

export interface OnePagerSummary {
  title: string;
  executive_summary: string;
  key_takeaways: string[];
  main_content: string;
}

export interface DetailedReadingMaterialSectionItem {
  title: string;
  content: string;
}

export interface DetailedReadingMaterial {
  title: string;
  introduction: string;
  sections: DetailedReadingMaterialSectionItem[];
  conclusion: string;
  references?: string[] | null;
}

export interface FAQItem {
  question: string;
  answer: string;
  category?: string | null;
}

export interface FAQCollection {
  title: string; // Pydantic has default
  items: FAQItem[];
}

export interface FlashcardItem {
  term: string;
  definition: string;
  category?: string | null;
  difficulty: 'easy' | 'medium' | 'hard' | string; // Pydantic has default
}

export interface FlashcardCollection {
  title: string; // Pydantic has default
  items: FlashcardItem[];
}

export interface ReadingGuideQuestions {
  title: string; // Pydantic has default
  questions: string[];
}

// --- Main GeneratedContent Interface (updated) ---
// This is the structure for the 'content' field in the main ContentResponse from backend
// or the 'result' field in the frontend JobResponse when job is complete.
export interface GeneratedContent {
  content_outline: ContentOutline; // Outline is mandatory
  podcast_script?: PodcastScript | null;
  study_guide?: StudyGuide | null;
  one_pager_summary?: OnePagerSummary | null;
  detailed_reading_material?: DetailedReadingMaterial | null;
  faqs?: FAQCollection | null;
  flashcards?: FlashcardCollection | null;
  reading_guide_questions?: ReadingGuideQuestions | null;
}

// --- Metadata and Metrics (matching Pydantic models) ---

export interface BackendContentMetadata { // Renamed to avoid clash if frontend JobMetadata is different
  source_syllabus_length?: number | null;
  source_format?: string | null;
  target_duration_minutes?: number | null;
  target_pages_count?: number | null;
  calculated_total_word_count?: number | null;
  calculated_total_duration?: number | null; // Not in Pydantic, but was in service return
  generation_timestamp: string; // ISO 8601 date string
  ai_model_used?: string | null;
  tokens_consumed?: number | null;
  estimated_cost?: number | null;
}

export interface QualityMetrics {
  overall_score?: number | null;
  readability_score?: number | null;
  structure_score?: number | null;
  relevance_score?: number | null;
  engagement_score?: number | null;
  format_compliance_score?: number | null;
  content_length_compliance?: boolean | null;
  validation_errors: string[];
}


// --- Job Request and Response Interfaces (frontend perspective) ---

// This JobMetadata is for the ContentGeneratorForm's state.
export interface JobMetadata {
  syllabus_text: string;
  requested_content_types: ContentType[]; // Used by the form
  target_audience?: string | null;
  difficulty?: 'beginner' | 'intermediate' | 'advanced' | string; // Used by the form
  length?: 'short' | 'medium' | 'long' | string; // Used by the form
  target_duration_minutes?: number | null;
  target_pages?: number | null; // Align with backend ContentRequest
  generate_audio?: boolean | null;
  target_format?: string; // Align with backend ContentRequest, though form might not set it directly for payload
}

export interface JobCreationRequest { // Maps to backend ContentRequest (ContentRequest model in pydantic/content.py)
  syllabus_text: string;
  target_format?: string;
  target_duration?: number | null; // Changed from target_duration_minutes for consistency
  target_pages?: number | null;
  // use_parallel and use_cache are backend concerns, not typically part of frontend request payload for job creation.
}


// --- Job Progress Interface (matching backend JobProgress schema) ---
export interface FrontendJobProgress {
  current_step: string;
  total_steps: number;
  completed_steps: number;
  percentage: number; // Overall progress percentage
  estimated_time_remaining?: number | null; // in seconds
}

// This JobResponse is likely for polling job status from /api/v1/jobs/{job_id}
export interface JobStatusPollResponse { // Renamed to distinguish from the final content payload
  id: string; // This is UUID on backend, but string in frontend is fine
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'partial' | 'cancelled'; // Added cancelled
  created_at: string; // ISO 8601 date string
  updated_at: string; // ISO 8601 date string
  completed_at?: string | null; // ISO 8601 date string
  error?: { // Aligning with backend JobError
    code: string; // JobErrorCode
    message: string;
    details?: Record<string, any> | null;
  } | null;
  progress?: FrontendJobProgress | null;
  // When status is 'completed' or 'partial', the result might contain the full content
  // or a pointer/ID to fetch it. Assuming it contains the full content for now.
  result?: GeneratedContent | null; // This is the detailed GeneratedContent
  metadata?: Record<string, any> | null; // Aligning with backend Job.metadata
  // The backend ContentResponse has a richer structure.
  // This JobStatusPollResponse might need to evolve to include fields like
  // version_id, quality_metrics, and the more detailed BackendContentMetadata
  // when the job is 'completed'.
}

// This interface represents the expected response when fetching a completed job's content,
// aligning with backend's ContentResponse Pydantic model.
export interface FullContentResponse {
  job_id?: string | null;
  content: GeneratedContent;
  metadata: BackendContentMetadata;
  quality_metrics?: QualityMetrics | null;
  version_id?: string | null;
  status: 'completed' | 'partial' | 'failed' | string; // Backend has 'completed', 'partial', 'failed'
  created_at: string; // ISO 8601 date string
}


// --- Old types (review if still needed or can be deprecated) ---
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

// --- API Error Interface ---
export interface ApiError {
  message: string; // Typically from error.response.data.detail or error.message
  code?: string | number; // HTTP status code or backend error code
  details?: Record<string, unknown> | Array<Record<string,unknown>>; // For validation errors etc.
}
