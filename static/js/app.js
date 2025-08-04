// La Factoria Frontend JavaScript
// Simple vanilla JS implementation for educational content generation

class LaFactoriaApp {
    constructor() {
        this.apiKey = localStorage.getItem('la-factoria-api-key') || '';
        this.baseURL = window.location.origin;
        this.currentContent = null;

        this.initializeApp();
    }

    initializeApp() {
        // Load saved API key
        const apiKeyInput = document.getElementById('apiKey');
        if (apiKeyInput && this.apiKey) {
            apiKeyInput.value = this.apiKey;
        }

        // Bind form submission
        const form = document.getElementById('contentForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmission(e));
        }

        // Auto-save API key
        if (apiKeyInput) {
            apiKeyInput.addEventListener('change', (e) => {
                this.apiKey = e.target.value;
                localStorage.setItem('la-factoria-api-key', this.apiKey);
            });
        }

        console.log('La Factoria app initialized');
    }

    async handleFormSubmission(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());

        // Validate required fields
        if (!data.apiKey || !data.topic || !data.contentType) {
            this.showError('Please fill in all required fields');
            return;
        }

        // Save API key
        this.apiKey = data.apiKey;
        localStorage.setItem('la-factoria-api-key', this.apiKey);

        // Show loading state
        this.setLoadingState(true);
        this.hideError();
        this.hideResults();

        try {
            const content = await this.generateContent(data);
            this.showResults(content);
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.setLoadingState(false);
        }
    }

    async generateContent(formData) {
        const requestBody = {
            topic: formData.topic,
            age_group: formData.ageGroup || 'general',
            additional_requirements: formData.requirements || null
        };

        const response = await fetch(`${this.baseURL}/api/v1/generate/${formData.contentType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            let errorMessage = 'Content generation failed';

            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                // Use default error message
            }

            throw new Error(`${errorMessage} (Status: ${response.status})`);
        }

        return await response.json();
    }

    showResults(content) {
        this.currentContent = content;

        // Update quality score
        const qualityScore = content.quality_metrics?.overall_quality_score || 0;
        document.getElementById('qualityScore').textContent = (qualityScore * 100).toFixed(1) + '%';

        // Update generation time
        const generationTime = content.metadata?.generation_duration_ms || 0;
        document.getElementById('generationTime').textContent = generationTime.toLocaleString();

        // Update content output
        const contentOutput = document.getElementById('contentOutput');
        if (contentOutput) {
            contentOutput.textContent = this.formatContent(content.generated_content);
        }

        // Show results section
        document.getElementById('resultsSection').style.display = 'block';

        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    formatContent(content) {
        if (typeof content === 'string') {
            return content;
        }

        if (typeof content === 'object') {
            return JSON.stringify(content, null, 2);
        }

        return String(content);
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');

        if (errorSection && errorMessage) {
            errorMessage.textContent = message;
            errorSection.style.display = 'block';

            // Scroll to error
            errorSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    hideError() {
        const errorSection = document.getElementById('errorSection');
        if (errorSection) {
            errorSection.style.display = 'none';
        }
    }

    hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
    }

    setLoadingState(isLoading) {
        const button = document.getElementById('generateBtn');
        const buttonText = button.querySelector('.btn-text');
        const buttonLoading = button.querySelector('.btn-loading');

        if (isLoading) {
            button.disabled = true;
            buttonText.style.display = 'none';
            buttonLoading.style.display = 'inline-flex';
        } else {
            button.disabled = false;
            buttonText.style.display = 'inline';
            buttonLoading.style.display = 'none';
        }
    }
}

// Global functions for button actions
function copyContent() {
    const contentOutput = document.getElementById('contentOutput');
    if (contentOutput) {
        const textToCopy = contentOutput.textContent;
        navigator.clipboard.writeText(textToCopy).then(() => {
            // Show temporary feedback
            const originalText = event.target.textContent;
            event.target.textContent = 'Copied!';
            setTimeout(() => {
                event.target.textContent = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy content:', err);
            alert('Failed to copy content to clipboard');
        });
    }
}

function downloadContent() {
    if (!window.laFactoriaApp || !window.laFactoriaApp.currentContent) {
        alert('No content to download');
        return;
    }

    const content = window.laFactoriaApp.currentContent;
    const contentText = window.laFactoriaApp.formatContent(content.generated_content);

    // Create filename
    const topic = content.topic.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    const contentType = content.content_type;
    const filename = `la_factoria_${contentType}_${topic}.txt`;

    // Create and download file
    const blob = new Blob([contentText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.laFactoriaApp = new LaFactoriaApp();
});

// Handle API key storage and management
function clearApiKey() {
    localStorage.removeItem('la-factoria-api-key');
    document.getElementById('apiKey').value = '';
    alert('API key cleared');
}

// Simple API key validation
function validateApiKey(apiKey) {
    if (!apiKey) return false;
    if (apiKey.length < 8) return false;
    return true;
}

// Error handling for network issues
window.addEventListener('online', () => {
    console.log('Network connection restored');
});

window.addEventListener('offline', () => {
    console.log('Network connection lost');
    alert('Network connection lost. Please check your internet connection.');
});

// Simple analytics (placeholder)
function trackEvent(eventName, properties = {}) {
    console.log('Event:', eventName, properties);
    // In production, this would integrate with analytics service
}

// Content type descriptions for better UX
const CONTENT_TYPE_DESCRIPTIONS = {
    'master_content_outline': 'Creates a comprehensive outline with learning objectives and content structure',
    'podcast_script': 'Generates conversational audio content with speaker notes and timing',
    'study_guide': 'Produces detailed study materials with key concepts and practice exercises',
    'one_pager_summary': 'Creates a concise one-page overview with essential information',
    'detailed_reading_material': 'Generates in-depth educational content with examples and explanations',
    'faq_collection': 'Creates frequently asked questions and comprehensive answers',
    'flashcards': 'Produces term-definition pairs optimized for memorization',
    'reading_guide_questions': 'Generates discussion questions for reading comprehension'
};

// Update content type description when selection changes
document.addEventListener('DOMContentLoaded', () => {
    const contentTypeSelect = document.getElementById('contentType');
    if (contentTypeSelect) {
        contentTypeSelect.addEventListener('change', (e) => {
            const description = CONTENT_TYPE_DESCRIPTIONS[e.target.value];
            console.log('Content type selected:', e.target.value, description);
        });
    }
});
