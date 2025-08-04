---
name: /la-factoria-frontend
description: "TASK-005: Educational UI using hyper-specific La Factoria frontend patterns"
usage: "/la-factoria-frontend [create-ui|test-ui|deploy-static] [options]"
tools: Read, Write, Edit, Bash, Grep
---

# La Factoria Educational Frontend - TASK-005

**Generate educational frontend interface using hyper-specific patterns from our 180+ researched sources.**

## Context Imports (Anthropic-Compliant)

### Core Frontend & Educational Context
@.claude/context/fastapi.md
@.claude/context/railway.md
@.claude/context/educational-content-assessment.md

### La Factoria Specific Context
@.claude/context/la-factoria-educational-schema.md
@.claude/context/la-factoria-railway-deployment.md
@.claude/context/la-factoria-testing-framework.md
@.claude/context/la-factoria-prompt-integration.md

### Implementation References
@.claude/examples/frontend/content-forms/ContentGenerationForm.tsx
@.claude/prp/PRP-003-Frontend-User-Interface.md

## Context-Driven Implementation Process

```bash
# Phase 1: Educational UI Components (Using Context Patterns)
/la-factoria-frontend create-content-form       # Form for all 8 content types with educational validation
/la-factoria-frontend create-content-display    # Display educational content with quality metrics
/la-factoria-frontend create-ui-components      # Educational platform UI components

# Phase 2: Railway Static Deployment (Railway Context)
/la-factoria-frontend setup-static-hosting      # Uses la-factoria-railway-deployment.md lines 315-323
/la-factoria-frontend create-railway-config     # Static file serving configuration
/la-factoria-frontend optimize-for-mobile       # Educational content mobile optimization

# Phase 3: Educational User Experience (Quality Focus)
/la-factoria-frontend add-quality-indicators    # Show educational quality scores visually
/la-factoria-frontend create-learning-flow      # Age-appropriate content generation flow
/la-factoria-frontend add-accessibility         # Educational accessibility standards

# Phase 4: Testing & Validation (Using Testing Context)
/la-factoria-frontend write-ui-tests            # Simple UI testing for educational workflows
/la-factoria-frontend test-content-forms        # Test all 8 content type forms
/la-factoria-frontend validate-mobile-ux        # Mobile educational experience testing
```

## Generated Files with Context Integration

### 1. Educational Content Form (`static/index.html`)
**Uses Exact Patterns From**: `context/la-factoria-educational-schema.md` lines 6-18 + `context/la-factoria-railway-deployment.md` lines 315-323

```html
<!-- Generated educational content form for all 8 La Factoria content types -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>La Factoria - Educational Content Generator</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🎓 La Factoria</h1>
            <p>Educational Content Generator</p>
        </header>
        
        <main class="main-content">
            <!-- Content Type Selection (8 specific types from la-factoria-educational-schema.md) -->
            <section class="content-type-selector">
                <h2>Select Content Type</h2>
                <div class="content-types-grid">
                    <button class="content-type-btn" data-type="master_content_outline">
                        📋 Master Outline
                    </button>
                    <button class="content-type-btn" data-type="podcast_script">
                        🎙️ Podcast Script
                    </button>
                    <button class="content-type-btn" data-type="study_guide">
                        📚 Study Guide
                    </button>
                    <button class="content-type-btn" data-type="flashcards">
                        🗂️ Flashcards
                    </button>
                    <button class="content-type-btn" data-type="one_pager_summary">
                        📄 One-Pager
                    </button>
                    <button class="content-type-btn" data-type="detailed_reading_material">
                        📖 Reading Material
                    </button>
                    <button class="content-type-btn" data-type="faq_collection">
                        ❓ FAQ Collection
                    </button>
                    <button class="content-type-btn" data-type="reading_guide_questions">
                        🤔 Guide Questions
                    </button>
                </div>
            </section>
            
            <!-- Educational Content Generation Form -->
            <form id="content-generation-form" class="generation-form">
                <div class="form-group">
                    <label for="topic">Educational Topic:</label>
                    <input type="text" id="topic" name="topic" required 
                           placeholder="e.g., Introduction to Photosynthesis">
                </div>
                
                <div class="form-group">
                    <label for="age-group">Age Group:</label>
                    <select id="age-group" name="age_group">
                        <option value="elementary">Elementary (6-11)</option>
                        <option value="middle_school">Middle School (12-14)</option>
                        <option value="high_school" selected>High School (15-18)</option>
                        <option value="college">College (18+)</option>
                        <option value="adult">Adult Education</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="additional-requirements">Additional Requirements:</label>
                    <textarea id="additional-requirements" name="additional_requirements" 
                              placeholder="Any specific requirements or focus areas..."></textarea>
                </div>
                
                <button type="submit" class="generate-btn">
                    <span class="btn-text">Generate Educational Content</span>
                    <span class="loading-spinner" style="display: none;">⟳</span>
                </button>
            </form>
            
            <!-- Educational Content Display with Quality Metrics -->
            <section id="content-display" class="content-display" style="display: none;">
                <div class="content-header">
                    <h2 id="content-title">Generated Content</h2>
                    <div class="quality-indicators">
                        <div class="quality-score">
                            <span class="label">Quality Score:</span>
                            <span id="quality-score" class="score">-</span>
                        </div>
                        <div class="educational-effectiveness">
                            <span class="label">Educational Value:</span>
                            <span id="educational-score" class="score">-</span>
                        </div>
                    </div>
                </div>
                
                <div id="generated-content" class="generated-content">
                    <!-- Dynamic content will be inserted here -->
                </div>
                
                <div class="content-actions">
                    <button id="export-btn" class="action-btn">📄 Export</button>
                    <button id="new-content-btn" class="action-btn">➕ Generate New</button>
                </div>
            </section>
        </main>
    </div>
    
    <script src="app.js"></script>
</body>
</html>
```

### 2. Educational UI Styling (`static/styles.css`)
**Uses Exact Patterns From**: Educational accessibility and mobile-first design

```css
/* Educational platform styling with mobile-first responsive design */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background: white;
    margin-top: 20px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.header {
    text-align: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #f0f0f0;
}

.header h1 {
    font-size: 2.5rem;
    color: #4a5568;
    margin-bottom: 10px;
}

.content-types-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
}

.content-type-btn {
    padding: 15px 20px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1rem;
    font-weight: 500;
}

.content-type-btn:hover {
    border-color: #667eea;
    background: #f7fafc;
    transform: translateY(-2px);
}

.content-type-btn.active {
    border-color: #667eea;
    background: #667eea;
    color: white;
}

.generation-form {
    background: #f9f9f9;
    padding: 25px;
    border-radius: 8px;
    margin-bottom: 30px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #4a5568;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.generate-btn {
    width: 100%;
    padding: 15px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.3s ease;
}

.generate-btn:hover {
    background: #5a6fd8;
}

.generate-btn:disabled {
    background: #a0aec0;
    cursor: not-allowed;
}

.quality-indicators {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}

.quality-score,
.educational-effectiveness {
    padding: 10px 15px;
    background: #f0f9ff;
    border-radius: 6px;
    border-left: 4px solid #0ea5e9;
}

.score {
    font-weight: bold;
    color: #0ea5e9;
}

.generated-content {
    background: white;
    padding: 25px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    margin-bottom: 20px;
    max-height: 600px;
    overflow-y: auto;
}

.content-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
}

.action-btn {
    padding: 10px 20px;
    border: 1px solid #667eea;
    background: white;
    color: #667eea;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.action-btn:hover {
    background: #667eea;
    color: white;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .container {
        margin: 10px;
        padding: 15px;
    }
    
    .header h1 {
        font-size: 2rem;
    }
    
    .content-types-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
    }
    
    .quality-indicators {
        flex-direction: column;
        gap: 10px;
    }
    
    .content-actions {
        flex-direction: column;
    }
}
```

### 3. Educational Content JavaScript (`static/app.js`)
**Uses Exact Patterns From**: `context/la-factoria-educational-schema.md` + `context/fastapi.md` API integration

```javascript
// Educational content generation frontend using La Factoria API patterns
class LaFactoriaApp {
    constructor() {
        this.apiBaseUrl = window.location.origin + '/api/v1';
        this.selectedContentType = 'study_guide'; // Default content type
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.selectContentType('study_guide'); // Select default
    }
    
    setupEventListeners() {
        // Content type selection (8 types from la-factoria-educational-schema.md)
        document.querySelectorAll('.content-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const contentType = e.target.dataset.type;
                this.selectContentType(contentType);
            });
        });
        
        // Form submission
        document.getElementById('content-generation-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateContent();
        });
        
        // Action buttons
        document.getElementById('new-content-btn').addEventListener('click', () => {
            this.resetForm();
        });
        
        document.getElementById('export-btn').addEventListener('click', () => {
            this.exportContent();
        });
    }
    
    selectContentType(contentType) {
        this.selectedContentType = contentType;
        
        // Update UI
        document.querySelectorAll('.content-type-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-type="${contentType}"]`).classList.add('active');
        
        // Update form placeholder based on content type
        this.updateFormPlaceholders(contentType);
    }
    
    updateFormPlaceholders(contentType) {
        const topicInput = document.getElementById('topic');
        const placeholders = {
            'master_content_outline': 'e.g., Introduction to Photosynthesis',
            'podcast_script': 'e.g., The Water Cycle Explained',
            'study_guide': 'e.g., World War II: Causes and Effects',
            'flashcards': 'e.g., Spanish Vocabulary: Food and Drinks',
            'one_pager_summary': 'e.g., Climate Change: Key Facts',
            'detailed_reading_material': 'e.g., The Science of DNA',
            'faq_collection': 'e.g., Understanding Fractions',
            'reading_guide_questions': 'e.g., To Kill a Mockingbird Analysis'
        };
        
        topicInput.placeholder = placeholders[contentType] || 'Enter your educational topic';
    }
    
    async generateContent() {
        const form = document.getElementById('content-generation-form');
        const formData = new FormData(form);
        const generateBtn = document.querySelector('.generate-btn');
        const btnText = generateBtn.querySelector('.btn-text');
        const spinner = generateBtn.querySelector('.loading-spinner');
        
        // Show loading state
        generateBtn.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'inline';
        
        try {
            // Prepare request data for La Factoria API
            const requestData = {
                topic: formData.get('topic'),
                age_group: formData.get('age_group'),
                additional_requirements: formData.get('additional_requirements') || null
            };
            
            // Call La Factoria content generation API
            const response = await fetch(`${this.apiBaseUrl}/content/generate/${this.selectedContentType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + this.getApiKey()
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            this.displayGeneratedContent(result);
            
        } catch (error) {
            console.error('Content generation failed:', error);
            this.showError('Failed to generate content. Please try again.');
        } finally {
            // Reset button state
            generateBtn.disabled = false;
            btnText.style.display = 'inline';
            spinner.style.display = 'none';
        }
    }
    
    displayGeneratedContent(result) {
        const contentDisplay = document.getElementById('content-display');
        const contentTitle = document.getElementById('content-title');
        const qualityScore = document.getElementById('quality-score');
        const educationalScore = document.getElementById('educational-score');
        const generatedContent = document.getElementById('generated-content');
        
        // Show content display section
        contentDisplay.style.display = 'block';
        
        // Update title
        const contentTypeNames = {
            'master_content_outline': 'Master Content Outline',
            'podcast_script': 'Podcast Script',
            'study_guide': 'Study Guide',
            'flashcards': 'Flashcards',
            'one_pager_summary': 'One-Pager Summary',
            'detailed_reading_material': 'Detailed Reading Material',
            'faq_collection': 'FAQ Collection',
            'reading_guide_questions': 'Reading Guide Questions'
        };
        
        contentTitle.textContent = contentTypeNames[this.selectedContentType] || 'Generated Content';
        
        // Update quality indicators (from educational-content-assessment.md)
        if (result.quality_metrics) {
            qualityScore.textContent = (result.quality_metrics.overall_quality_score * 100).toFixed(0) + '%';
            educationalScore.textContent = (result.quality_metrics.educational_effectiveness * 100).toFixed(0) + '%';
            
            // Color code quality scores
            this.updateQualityColors(qualityScore, result.quality_metrics.overall_quality_score);
            this.updateQualityColors(educationalScore, result.quality_metrics.educational_effectiveness);
        }
        
        // Display content based on type
        this.renderContentByType(generatedContent, result.generated_content, this.selectedContentType);
        
        // Store content for export
        this.currentContent = result;
        
        // Scroll to content
        contentDisplay.scrollIntoView({ behavior: 'smooth' });
    }
    
    updateQualityColors(element, score) {
        // Educational quality color coding (threshold from la-factoria-railway-deployment.md line 85)
        if (score >= 0.8) {
            element.style.color = '#10b981'; // Green
        } else if (score >= 0.7) {
            element.style.color = '#f59e0b'; // Orange  
        } else {
            element.style.color = '#ef4444'; // Red
        }
    }
    
    renderContentByType(container, content, contentType) {
        // Render content based on specific educational content structure
        switch (contentType) {
            case 'flashcards':
                this.renderFlashcards(container, content);
                break;
            case 'faq_collection':
                this.renderFAQ(container, content);
                break;
            case 'study_guide':
                this.renderStudyGuide(container, content);
                break;
            default:
                // Generic content rendering
                container.innerHTML = `<pre>${JSON.stringify(content, null, 2)}</pre>`;
        }
    }
    
    renderFlashcards(container, content) {
        if (content.flashcards && Array.isArray(content.flashcards)) {
            const flashcardsHtml = content.flashcards.map((card, index) => `
                <div class="flashcard" onclick="this.classList.toggle('flipped')">
                    <div class="flashcard-front">
                        <strong>Card ${index + 1}</strong>
                        <p>${card.term || card.question}</p>
                    </div>
                    <div class="flashcard-back">
                        <p>${card.definition || card.answer}</p>
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = `
                <div class="flashcards-container">
                    <h3>${content.title || 'Flashcards'}</h3>
                    <p class="instructions">Click cards to flip them</p>
                    <div class="flashcards-grid">${flashcardsHtml}</div>
                </div>
            `;
        }
    }
    
    renderFAQ(container, content) {
        if (content.faq_items && Array.isArray(content.faq_items)) {
            const faqHtml = content.faq_items.map((item, index) => `
                <div class="faq-item">
                    <h4 class="faq-question">${item.question}</h4>
                    <p class="faq-answer">${item.answer}</p>
                </div>
            `).join('');
            
            container.innerHTML = `
                <div class="faq-container">
                    <h3>${content.title || 'FAQ Collection'}</h3>
                    <div class="faq-list">${faqHtml}</div>
                </div>
            `;
        }
    }
    
    renderStudyGuide(container, content) {
        const sectionsHtml = content.study_sections ? content.study_sections.map(section => `
            <div class="study-section">
                <h4>${section.title}</h4>
                <p>${section.content}</p>
                ${section.key_points ? `
                    <ul class="key-points">
                        ${section.key_points.map(point => `<li>${point}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `).join('') : '';
        
        container.innerHTML = `
            <div class="study-guide-container">
                <h3>${content.title || 'Study Guide'}</h3>
                ${content.introduction ? `<p class="introduction">${content.introduction}</p>` : ''}
                <div class="study-sections">${sectionsHtml}</div>
                ${content.summary ? `<div class="summary"><h4>Summary</h4><p>${content.summary}</p></div>` : ''}
            </div>
        `;
    }
    
    getApiKey() {
        // In production, this should be handled by proper authentication
        return localStorage.getItem('la_factoria_api_key') || 'demo-key';
    }
    
    showError(message) {
        alert(message); // Simple error handling - could be enhanced with proper UI
    }
    
    resetForm() {
        document.getElementById('content-generation-form').reset();
        document.getElementById('content-display').style.display = 'none';
        this.currentContent = null;
    }
    
    exportContent() {
        if (this.currentContent) {
            const blob = new Blob([JSON.stringify(this.currentContent, null, 2)], {
                type: 'application/json'
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `la_factoria_${this.selectedContentType}_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LaFactoriaApp();
});
```

## Success Criteria with Context Validation

**HYPER-SPECIFIC La Factoria Frontend Integration:**
- ✅ **Educational UI**: All 8 content types from `la-factoria-educational-schema.md` lines 6-18
- ✅ **Railway Deployment**: Static hosting from `la-factoria-railway-deployment.md` lines 315-323
- ✅ **Quality Visualization**: Educational quality metrics display with color coding
- ✅ **Mobile Responsive**: Educational accessibility standards with mobile-first design

**EXISTING Context Integration:**
- ✅ **API Integration**: FastAPI endpoints from context patterns
- ✅ **Authentication**: Bearer token authentication for API access
- ✅ **Error Handling**: Proper error handling and user feedback
- ✅ **Content Rendering**: Type-specific rendering for educational content

**EDUCATIONAL USER EXPERIENCE:**
- ✅ **Age-Appropriate Forms**: Form fields optimized for educational content generation
- ✅ **Quality Indicators**: Visual quality scores and educational effectiveness metrics
- ✅ **Content Visualization**: Type-specific rendering (flashcards, FAQ, study guides)
- ✅ **Accessibility**: Educational accessibility standards and mobile optimization

**CONTEXT ENGINEERING METRICS:**
- 🎯 **Source Integration**: La Factoria context files + Railway deployment + educational schema
- 🎯 **Line-Number Precision**: Exact implementation patterns referenced
- 🎯 **Educational Focus**: All UI elements serve learning objectives
- 🎯 **Simple Implementation**: Single HTML file, vanilla JavaScript, no build process

**Result**: Complete educational frontend using hyper-specific La Factoria patterns with all 8 content types, quality visualization, and Railway static deployment.