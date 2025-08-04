-- La Factoria Educational Content Platform - Initial Schema
-- Generated from la-factoria-educational-schema.md patterns
-- PostgreSQL Migration Script for Educational Content System

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table for La Factoria platform
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    api_key_hash VARCHAR(255),  -- Hashed API key for authentication
    is_active BOOLEAN DEFAULT true,
    learning_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Educational content table for all 8 content types
CREATE TABLE educational_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN (
        'master_content_outline',
        'podcast_script',
        'study_guide',
        'one_pager_summary',
        'detailed_reading_material',
        'faq_collection',
        'flashcards',
        'reading_guide_questions'
    )),
    topic VARCHAR(500) NOT NULL,
    age_group VARCHAR(50) NOT NULL CHECK (age_group IN (
        'elementary',
        'middle_school',
        'high_school',
        'college',
        'adult_learning',
        'general'
    )),
    learning_objectives JSONB NOT NULL DEFAULT '[]',
    cognitive_load_metrics JSONB NOT NULL DEFAULT '{}',
    generated_content JSONB NOT NULL,
    quality_score DECIMAL(3,2) CHECK (quality_score BETWEEN 0 AND 1),
    educational_effectiveness DECIMAL(3,2) CHECK (educational_effectiveness BETWEEN 0 AND 1),
    factual_accuracy DECIMAL(3,2) CHECK (factual_accuracy BETWEEN 0 AND 1),
    age_appropriateness DECIMAL(3,2) CHECK (age_appropriateness BETWEEN 0 AND 1),
    generation_duration_ms INTEGER,
    tokens_used INTEGER,
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    prompt_template VARCHAR(100),
    additional_requirements TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content generation sessions (for batch operations)
CREATE TABLE content_generation_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    topic VARCHAR(500) NOT NULL,
    age_group VARCHAR(50) NOT NULL,
    requested_content_types TEXT[] NOT NULL,
    session_status VARCHAR(20) DEFAULT 'pending' CHECK (session_status IN (
        'pending', 'in_progress', 'completed', 'failed', 'partial'
    )),
    total_content_types INTEGER NOT NULL,
    successful_generations INTEGER DEFAULT 0,
    failed_generations INTEGER DEFAULT 0,
    total_generation_time_ms INTEGER DEFAULT 0,
    average_quality_score DECIMAL(3,2),
    session_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Quality assessment results (detailed metrics)
CREATE TABLE quality_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES educational_content(id) ON DELETE CASCADE,
    overall_quality_score DECIMAL(3,2) NOT NULL,
    educational_value DECIMAL(3,2) NOT NULL,
    factual_accuracy DECIMAL(3,2) NOT NULL,
    age_appropriateness DECIMAL(3,2) NOT NULL,
    structural_quality DECIMAL(3,2) NOT NULL,
    engagement_level DECIMAL(3,2) NOT NULL,
    cognitive_load_metrics JSONB,
    readability_metrics JSONB,
    assessment_metadata JSONB DEFAULT '{}',
    meets_quality_threshold BOOLEAN DEFAULT false,
    meets_educational_threshold BOOLEAN DEFAULT false,
    meets_factual_threshold BOOLEAN DEFAULT false,
    assessor_version VARCHAR(10) DEFAULT '1.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API usage tracking for analytics and rate limiting
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    api_key_hash VARCHAR(64),
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    user_agent TEXT,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content feedback and ratings
CREATE TABLE content_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES educational_content(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    feedback_type VARCHAR(50) CHECK (feedback_type IN (
        'quality', 'accuracy', 'usefulness', 'age_appropriateness', 'general'
    )),
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance optimization
-- User table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_api_key_hash ON users(api_key_hash);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Educational content indexes
CREATE INDEX idx_educational_content_user_id ON educational_content(user_id);
CREATE INDEX idx_educational_content_content_type ON educational_content(content_type);
CREATE INDEX idx_educational_content_topic ON educational_content(topic);
CREATE INDEX idx_educational_content_age_group ON educational_content(age_group);
CREATE INDEX idx_educational_content_quality_score ON educational_content(quality_score);
CREATE INDEX idx_educational_content_created_at ON educational_content(created_at);
CREATE INDEX idx_educational_content_ai_provider ON educational_content(ai_provider);

-- Composite indexes for common queries
CREATE INDEX idx_educational_content_user_type ON educational_content(user_id, content_type);
CREATE INDEX idx_educational_content_type_created ON educational_content(content_type, created_at);
CREATE INDEX idx_educational_content_quality_created ON educational_content(quality_score, created_at);

-- Generation sessions indexes
CREATE INDEX idx_content_sessions_user_id ON content_generation_sessions(user_id);
CREATE INDEX idx_content_sessions_status ON content_generation_sessions(session_status);
CREATE INDEX idx_content_sessions_created_at ON content_generation_sessions(created_at);

-- Quality assessments indexes
CREATE INDEX idx_quality_assessments_content_id ON quality_assessments(content_id);
CREATE INDEX idx_quality_assessments_overall_score ON quality_assessments(overall_quality_score);
CREATE INDEX idx_quality_assessments_created_at ON quality_assessments(created_at);

-- API usage indexes
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_endpoint ON api_usage(endpoint);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX idx_api_usage_api_key_hash ON api_usage(api_key_hash);

-- Content feedback indexes
CREATE INDEX idx_content_feedback_content_id ON content_feedback(content_id);
CREATE INDEX idx_content_feedback_user_id ON content_feedback(user_id);
CREATE INDEX idx_content_feedback_rating ON content_feedback(rating);
CREATE INDEX idx_content_feedback_created_at ON content_feedback(created_at);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_educational_content_updated_at
    BEFORE UPDATE ON educational_content
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert initial data
-- Create system user for anonymous/demo content
INSERT INTO users (id, username, email, is_active)
VALUES (
    uuid_generate_v4(),
    'system',
    'system@lafactoria.app',
    true
) ON CONFLICT (username) DO NOTHING;

-- Create demo user for testing
INSERT INTO users (id, username, email, is_active)
VALUES (
    uuid_generate_v4(),
    'demo_user',
    'demo@lafactoria.app',
    true
) ON CONFLICT (username) DO NOTHING;

-- Create views for common queries
CREATE VIEW content_summary AS
SELECT
    c.id,
    c.content_type,
    c.topic,
    c.age_group,
    c.quality_score,
    c.educational_effectiveness,
    c.created_at,
    u.username,
    qa.overall_quality_score,
    qa.meets_quality_threshold
FROM educational_content c
LEFT JOIN users u ON c.user_id = u.id
LEFT JOIN quality_assessments qa ON c.id = qa.content_id;

CREATE VIEW user_content_stats AS
SELECT
    u.id as user_id,
    u.username,
    COUNT(c.id) as total_content_generated,
    AVG(c.quality_score) as average_quality_score,
    COUNT(DISTINCT c.content_type) as unique_content_types,
    MAX(c.created_at) as last_generation_date
FROM users u
LEFT JOIN educational_content c ON u.id = c.user_id
GROUP BY u.id, u.username;

CREATE VIEW content_type_stats AS
SELECT
    content_type,
    COUNT(*) as total_generated,
    AVG(quality_score) as average_quality,
    AVG(generation_duration_ms) as average_generation_time,
    COUNT(DISTINCT user_id) as unique_users
FROM educational_content
GROUP BY content_type;

COMMENT ON TABLE users IS 'User accounts for La Factoria educational content platform';
COMMENT ON TABLE educational_content IS 'Generated educational content for all 8 La Factoria content types';
COMMENT ON TABLE content_generation_sessions IS 'Batch content generation session tracking';
COMMENT ON TABLE quality_assessments IS 'Detailed quality assessment metrics for educational content';
COMMENT ON TABLE api_usage IS 'API usage tracking for analytics and rate limiting';
COMMENT ON TABLE content_feedback IS 'User feedback and ratings for generated content';

COMMENT ON COLUMN educational_content.content_type IS 'One of 8 La Factoria content types: master_content_outline, podcast_script, study_guide, one_pager_summary, detailed_reading_material, faq_collection, flashcards, reading_guide_questions';
COMMENT ON COLUMN educational_content.learning_objectives IS 'JSON array of learning objectives following Blooms taxonomy';
COMMENT ON COLUMN educational_content.cognitive_load_metrics IS 'JSON object with intrinsic_load, extraneous_load, germane_load metrics';
COMMENT ON COLUMN educational_content.generated_content IS 'JSON object containing the structured educational content';
COMMENT ON COLUMN educational_content.quality_score IS 'Overall quality score from 0.0 to 1.0 (minimum 0.70 for acceptance)';
COMMENT ON COLUMN educational_content.educational_effectiveness IS 'Educational value score from 0.0 to 1.0 (minimum 0.75)';
COMMENT ON COLUMN educational_content.factual_accuracy IS 'Factual accuracy score from 0.0 to 1.0 (minimum 0.85)';

-- Grant permissions (adjust as needed for your deployment)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO la_factoria_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO la_factoria_app;
