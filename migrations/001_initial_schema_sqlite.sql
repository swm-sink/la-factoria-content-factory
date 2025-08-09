-- La Factoria Educational Content Platform - SQLite Initial Schema
-- Adapted from PostgreSQL schema for development environment
-- SQLite Migration Script for Educational Content System

-- Users table for La Factoria platform
CREATE TABLE users (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    api_key_hash TEXT,  -- Hashed API key for authentication
    is_active BOOLEAN DEFAULT 1,
    learning_preferences TEXT DEFAULT '{}', -- JSON as TEXT in SQLite
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Educational content table for all 8 content types
CREATE TABLE educational_content (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    content_type TEXT NOT NULL CHECK (content_type IN (
        'master_content_outline',
        'podcast_script',
        'study_guide',
        'one_pager_summary',
        'detailed_reading_material',
        'faq_collection',
        'flashcards',
        'reading_guide_questions'
    )),
    topic TEXT NOT NULL,
    age_group TEXT NOT NULL CHECK (age_group IN (
        'elementary',
        'middle_school',
        'high_school',
        'college',
        'adult_learning',
        'general'
    )),
    learning_objectives TEXT NOT NULL DEFAULT '[]', -- JSON as TEXT
    cognitive_load_metrics TEXT NOT NULL DEFAULT '{}', -- JSON as TEXT
    generated_content TEXT NOT NULL, -- JSON as TEXT
    quality_score REAL CHECK (quality_score BETWEEN 0 AND 1),
    educational_effectiveness REAL CHECK (educational_effectiveness BETWEEN 0 AND 1),
    factual_accuracy REAL CHECK (factual_accuracy BETWEEN 0 AND 1),
    age_appropriateness REAL CHECK (age_appropriateness BETWEEN 0 AND 1),
    generation_duration_ms INTEGER,
    tokens_used INTEGER,
    ai_provider TEXT,
    ai_model TEXT,
    prompt_template TEXT,
    additional_requirements TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Content generation sessions (for batch operations)
CREATE TABLE content_generation_sessions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    age_group TEXT NOT NULL,
    requested_content_types TEXT NOT NULL, -- JSON array as TEXT
    session_status TEXT DEFAULT 'pending' CHECK (session_status IN (
        'pending', 'in_progress', 'completed', 'failed', 'partial'
    )),
    total_content_types INTEGER NOT NULL,
    successful_generations INTEGER DEFAULT 0,
    failed_generations INTEGER DEFAULT 0,
    total_generation_time_ms INTEGER DEFAULT 0,
    average_quality_score REAL,
    session_metadata TEXT DEFAULT '{}', -- JSON as TEXT
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

-- Quality assessment results (detailed metrics)
CREATE TABLE quality_assessments (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    content_id TEXT REFERENCES educational_content(id) ON DELETE CASCADE,
    overall_quality_score REAL NOT NULL,
    educational_value REAL NOT NULL,
    factual_accuracy REAL NOT NULL,
    age_appropriateness REAL NOT NULL,
    structural_quality REAL NOT NULL,
    engagement_level REAL NOT NULL,
    cognitive_load_metrics TEXT, -- JSON as TEXT
    readability_metrics TEXT, -- JSON as TEXT
    assessment_metadata TEXT DEFAULT '{}', -- JSON as TEXT
    meets_quality_threshold BOOLEAN DEFAULT 0,
    meets_educational_threshold BOOLEAN DEFAULT 0,
    meets_factual_threshold BOOLEAN DEFAULT 0,
    assessor_version TEXT DEFAULT '1.0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- API usage tracking for analytics and rate limiting
CREATE TABLE api_usage (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    api_key_hash TEXT,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    user_agent TEXT,
    ip_address TEXT, -- Store IP as TEXT in SQLite
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Content feedback and ratings
CREATE TABLE content_feedback (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    content_id TEXT REFERENCES educational_content(id) ON DELETE CASCADE,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    feedback_type TEXT CHECK (feedback_type IN (
        'quality', 'accuracy', 'usefulness', 'age_appropriateness', 'general'
    )),
    is_public BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

-- SQLite triggers for updated_at timestamps (different syntax than PostgreSQL)
CREATE TRIGGER update_users_updated_at
    AFTER UPDATE ON users
    FOR EACH ROW
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_educational_content_updated_at
    AFTER UPDATE ON educational_content
    FOR EACH ROW
    BEGIN
        UPDATE educational_content SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Insert initial data
-- Create system user for anonymous/demo content
INSERT OR IGNORE INTO users (id, username, email, is_active)
VALUES (
    lower(hex(randomblob(16))),
    'system',
    'system@lafactoria.app',
    1
);

-- Create demo user for testing
INSERT OR IGNORE INTO users (id, username, email, is_active)
VALUES (
    lower(hex(randomblob(16))),
    'demo_user',
    'demo@lafactoria.app',
    1
);

-- Create views for common queries (SQLite syntax)
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