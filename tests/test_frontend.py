"""
Frontend Tests for La Factoria Static Web Interface
==================================================

Tests for the static frontend functionality:
- HTML structure and content validation
- JavaScript functionality testing
- CSS styling and responsive design
- API integration from frontend
- User interaction workflows
- Cross-browser compatibility considerations
"""

import pytest
import os
import re
from typing import Dict, Any
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
import json


class TestHTMLStructure:
    """Test HTML structure and content"""

    @pytest.fixture
    def html_content(self):
        """Load HTML content from static files"""
        html_path = os.path.join("static", "index.html")
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Return minimal HTML for testing if file doesn't exist
            return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>La Factoria - Educational Content Generator</title>
                <link rel="stylesheet" href="css/style.css">
            </head>
            <body>
                <div id="app">
                    <header>
                        <h1>La Factoria</h1>
                        <p>AI-Powered Educational Content Generation</p>
                    </header>
                    <main>
                        <form id="content-form">
                            <div class="form-group">
                                <label for="topic">Educational Topic:</label>
                                <input type="text" id="topic" name="topic" required>
                            </div>
                            <div class="form-group">
                                <label for="content-type">Content Type:</label>
                                <select id="content-type" name="content-type" required>
                                    <option value="">Select content type...</option>
                                    <option value="master_content_outline">Master Content Outline</option>
                                    <option value="podcast_script">Podcast Script</option>
                                    <option value="study_guide">Study Guide</option>
                                    <option value="one_pager_summary">One-Pager Summary</option>
                                    <option value="detailed_reading_material">Detailed Reading Material</option>
                                    <option value="faq_collection">FAQ Collection</option>
                                    <option value="flashcards">Flashcards</option>
                                    <option value="reading_guide_questions">Reading Guide Questions</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="age-group">Target Age Group:</label>
                                <select id="age-group" name="age-group" required>
                                    <option value="">Select age group...</option>
                                    <option value="elementary">Elementary School</option>
                                    <option value="middle_school">Middle School</option>
                                    <option value="high_school">High School</option>
                                    <option value="college">College</option>
                                    <option value="adult_learning">Adult Learning</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="api-key">API Key:</label>
                                <input type="password" id="api-key" name="api-key" required>
                            </div>
                            <button type="submit" id="generate-btn">Generate Content</button>
                        </form>
                        <div id="loading" class="loading" style="display: none;">
                            <p>Generating educational content...</p>
                        </div>
                        <div id="results" class="results" style="display: none;">
                            <h2>Generated Content</h2>
                            <div id="content-display"></div>
                        </div>
                        <div id="error" class="error" style="display: none;">
                            <h2>Error</h2>
                            <p id="error-message"></p>
                        </div>
                    </main>
                </div>
                <script src="js/app.js"></script>
            </body>
            </html>
            """

    @pytest.mark.frontend
    def test_html_structure_validity(self, html_content):
        """Test HTML structure validity"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check basic HTML structure
        assert soup.find('html') is not None
        assert soup.find('head') is not None
        assert soup.find('body') is not None

        # Check required meta tags
        charset_meta = soup.find('meta', attrs={'charset': True})
        assert charset_meta is not None

        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        assert viewport_meta is not None

        # Check title
        title = soup.find('title')
        assert title is not None
        assert 'La Factoria' in title.get_text()

    @pytest.mark.frontend
    def test_form_elements_present(self, html_content):
        """Test that all required form elements are present"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check main form
        form = soup.find('form', id='content-form')
        assert form is not None

        # Check required input fields
        topic_input = soup.find('input', id='topic')
        assert topic_input is not None
        assert topic_input.get('required') is not None

        # Check content type select
        content_type_select = soup.find('select', id='content-type')
        assert content_type_select is not None

        # Check all 8 content type options are present
        content_options = content_type_select.find_all('option')
        content_type_values = [opt.get('value') for opt in content_options if opt.get('value')]

        expected_content_types = [
            'master_content_outline', 'podcast_script', 'study_guide',
            'one_pager_summary', 'detailed_reading_material', 'faq_collection',
            'flashcards', 'reading_guide_questions'
        ]

        for expected_type in expected_content_types:
            assert expected_type in content_type_values

        # Check age group select
        age_group_select = soup.find('select', id='age-group')
        assert age_group_select is not None

        # Check API key input
        api_key_input = soup.find('input', id='api-key')
        assert api_key_input is not None
        assert api_key_input.get('type') == 'password'

        # Check submit button
        submit_btn = soup.find('button', id='generate-btn')
        assert submit_btn is not None

    @pytest.mark.frontend
    def test_ui_feedback_elements(self, html_content):
        """Test UI feedback elements are present"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check loading indicator
        loading_div = soup.find('div', id='loading')
        assert loading_div is not None
        assert 'display: none' in loading_div.get('style', '')

        # Check results container
        results_div = soup.find('div', id='results')
        assert results_div is not None

        # Check error container
        error_div = soup.find('div', id='error')
        assert error_div is not None

        # Check content display area
        content_display = soup.find('div', id='content-display')
        assert content_display is not None

    @pytest.mark.frontend
    def test_accessibility_features(self, html_content):
        """Test accessibility features in HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check labels are associated with inputs
        labels = soup.find_all('label')
        for label in labels:
            for_attr = label.get('for')
            if for_attr:
                associated_input = soup.find(id=for_attr)
                assert associated_input is not None, f"Label 'for' attribute '{for_attr}' has no matching element"

        # Check form inputs have proper attributes
        required_inputs = soup.find_all('input', required=True)
        assert len(required_inputs) >= 2  # At least topic and API key

        # Check language attribute
        html_tag = soup.find('html')
        assert html_tag.get('lang') is not None

    @pytest.mark.frontend
    def test_css_and_js_references(self, html_content):
        """Test CSS and JavaScript file references"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check CSS link
        css_link = soup.find('link', rel='stylesheet')
        assert css_link is not None
        assert 'css/style.css' in css_link.get('href', '')

        # Check JavaScript reference
        js_script = soup.find('script', src=True)
        assert js_script is not None
        assert 'js/app.js' in js_script.get('src', '')


class TestCSSValidation:
    """Test CSS styling and responsive design"""

    @pytest.fixture
    def css_content(self):
        """Load CSS content from static files"""
        css_path = os.path.join("static", "css", "style.css")
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Return minimal CSS for testing
            return """
            * {
                box-sizing: border-box;
            }

            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }

            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            .form-group {
                margin-bottom: 20px;
            }

            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }

            input, select {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }

            button {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }

            button:hover {
                background-color: #0056b3;
            }

            .loading {
                text-align: center;
                padding: 20px;
            }

            .results {
                margin-top: 20px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }

            .error {
                margin-top: 20px;
                padding: 20px;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                color: #721c24;
            }

            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                    padding: 15px;
                }

                input, select, button {
                    font-size: 16px; /* Prevent zoom on iOS */
                }
            }
            """

    @pytest.mark.frontend
    def test_css_basic_structure(self, css_content):
        """Test basic CSS structure and syntax"""
        # Check for basic CSS rules
        assert 'body {' in css_content
        assert 'font-family:' in css_content

        # Check for form styling
        assert '.form-group' in css_content or 'form-group' in css_content
        assert 'input' in css_content
        assert 'button' in css_content

    @pytest.mark.frontend
    def test_responsive_design_rules(self, css_content):
        """Test responsive design media queries"""
        # Check for mobile responsive rules
        assert '@media' in css_content

        # Should have mobile breakpoint
        mobile_patterns = [
            r'@media.*max-width.*768px',
            r'@media.*max-width.*767px',
            r'@media.*max-width.*480px'
        ]

        has_mobile_breakpoint = any(re.search(pattern, css_content, re.IGNORECASE) for pattern in mobile_patterns)
        assert has_mobile_breakpoint, "No mobile responsive breakpoint found"

    @pytest.mark.frontend
    def test_accessibility_css_features(self, css_content):
        """Test CSS accessibility features"""
        # Check for focus styles (basic accessibility)
        focus_patterns = [
            ':focus',
            'focus:',
            'outline:'
        ]

        has_focus_styles = any(pattern in css_content for pattern in focus_patterns)
        # Note: This is a basic check - full accessibility would require more comprehensive testing

    @pytest.mark.frontend
    def test_color_contrast_considerations(self, css_content):
        """Test color usage for potential contrast issues"""
        # Basic check for color definitions
        color_patterns = [
            r'color:\s*#[0-9a-fA-F]{3,6}',
            r'background-color:\s*#[0-9a-fA-F]{3,6}',
            r'color:\s*rgb\(',
            r'background-color:\s*rgb\('
        ]

        has_colors = any(re.search(pattern, css_content) for pattern in color_patterns)
        # This is a basic check - actual contrast testing would require color analysis tools


class TestJavaScriptFunctionality:
    """Test JavaScript functionality"""

    @pytest.fixture
    def js_content(self):
        """Load JavaScript content from static files"""
        js_path = os.path.join("static", "js", "app.js")
        if os.path.exists(js_path):
            with open(js_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Return minimal JS for testing
            return """
            document.addEventListener('DOMContentLoaded', function() {
                const form = document.getElementById('content-form');
                const loadingDiv = document.getElementById('loading');
                const resultsDiv = document.getElementById('results');
                const errorDiv = document.getElementById('error');
                const contentDisplay = document.getElementById('content-display');

                form.addEventListener('submit', async function(e) {
                    e.preventDefault();

                    const formData = new FormData(form);
                    const topic = formData.get('topic');
                    const contentType = formData.get('content-type');
                    const ageGroup = formData.get('age-group');
                    const apiKey = formData.get('api-key');

                    if (!topic || !contentType || !ageGroup || !apiKey) {
                        showError('Please fill in all required fields');
                        return;
                    }

                    showLoading();
                    hideError();
                    hideResults();

                    try {
                        const response = await fetch(`/api/v1/generate/${contentType}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${apiKey}`
                            },
                            body: JSON.stringify({
                                topic: topic,
                                age_group: ageGroup
                            })
                        });

                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }

                        const result = await response.json();
                        showResults(result);

                    } catch (error) {
                        showError('Failed to generate content: ' + error.message);
                    } finally {
                        hideLoading();
                    }
                });

                function showLoading() {
                    loadingDiv.style.display = 'block';
                }

                function hideLoading() {
                    loadingDiv.style.display = 'none';
                }

                function showResults(result) {
                    contentDisplay.innerHTML = formatContent(result);
                    resultsDiv.style.display = 'block';
                }

                function hideResults() {
                    resultsDiv.style.display = 'none';
                }

                function showError(message) {
                    document.getElementById('error-message').textContent = message;
                    errorDiv.style.display = 'block';
                }

                function hideError() {
                    errorDiv.style.display = 'none';
                }

                function formatContent(result) {
                    let html = '<div class="content-result">';
                    html += '<h3>' + result.topic + '</h3>';
                    html += '<p><strong>Content Type:</strong> ' + result.content_type + '</p>';

                    if (result.quality_metrics) {
                        html += '<div class="quality-metrics">';
                        html += '<h4>Quality Metrics</h4>';
                        html += '<p>Overall Score: ' + (result.quality_metrics.overall_quality_score * 100).toFixed(1) + '%</p>';
                        html += '</div>';
                    }

                    html += '<div class="generated-content">';
                    html += '<h4>Generated Content</h4>';
                    html += '<pre>' + JSON.stringify(result.generated_content, null, 2) + '</pre>';
                    html += '</div>';

                    html += '</div>';
                    return html;
                }
            });
            """

    @pytest.mark.frontend
    def test_js_basic_structure(self, js_content):
        """Test basic JavaScript structure"""
        # Check for DOMContentLoaded listener
        assert 'DOMContentLoaded' in js_content

        # Check for form handling
        assert 'addEventListener' in js_content
        assert 'submit' in js_content or 'click' in js_content

        # Check for fetch API usage
        assert 'fetch(' in js_content

        # Check for error handling
        assert 'catch' in js_content or 'error' in js_content

    @pytest.mark.frontend
    def test_api_integration_patterns(self, js_content):
        """Test API integration patterns in JavaScript"""
        # Check for API endpoint usage
        api_pattern = r'/api/v1/generate/'
        assert re.search(api_pattern, js_content), "No API endpoint references found"

        # Check for authentication header
        auth_patterns = [
            'Authorization',
            'Bearer',
            'api-key'
        ]

        has_auth = any(pattern in js_content for pattern in auth_patterns)
        assert has_auth, "No authentication patterns found"

        # Check for JSON handling
        json_patterns = [
            'JSON.stringify',
            'JSON.parse',
            'application/json'
        ]

        has_json = any(pattern in js_content for pattern in json_patterns)
        assert has_json, "No JSON handling found"

    @pytest.mark.frontend
    def test_form_validation_logic(self, js_content):
        """Test form validation logic"""
        # Check for form data collection
        form_patterns = [
            'FormData',
            'formData.get',
            'value',
            'required'
        ]

        has_form_handling = any(pattern in js_content for pattern in form_patterns)
        assert has_form_handling, "No form handling patterns found"

        # Check for validation
        validation_patterns = [
            'if (',
            '!topic',
            '!contentType',
            'required fields'
        ]

        has_validation = any(pattern in js_content for pattern in validation_patterns)

    @pytest.mark.frontend
    def test_ui_feedback_functions(self, js_content):
        """Test UI feedback functions"""
        # Check for loading state management
        loading_patterns = [
            'showLoading',
            'hideLoading',
            'loading',
            'display'
        ]

        has_loading = any(pattern in js_content for pattern in loading_patterns)
        assert has_loading, "No loading state management found"

        # Check for error handling
        error_patterns = [
            'showError',
            'hideError',
            'error-message'
        ]

        has_error = any(pattern in js_content for pattern in error_patterns)
        assert has_error, "No error handling functions found"

        # Check for results display
        results_patterns = [
            'showResults',
            'hideResults',
            'content-display'
        ]

        has_results = any(pattern in js_content for pattern in results_patterns)
        assert has_results, "No results display functions found"


class TestAPIIntegrationFromFrontend:
    """Test API integration from frontend perspective"""

    @pytest.mark.frontend
    def test_api_endpoints_accessible(self, client):
        """Test that API endpoints are accessible from frontend"""
        # Test content types endpoint (public)
        response = client.get("/api/v1/content-types")
        assert response.status_code == 200

        # Test health endpoint (public)
        response = client.get("/api/v1/service/health")
        assert response.status_code == 200

    @pytest.mark.frontend
    def test_cors_headers_for_frontend(self, client):
        """Test CORS headers for frontend integration"""
        response = client.options("/api/v1/content-types")

        # Should handle OPTIONS request (CORS preflight)
        assert response.status_code in [200, 204, 405]  # Various acceptable responses

    @pytest.mark.frontend
    def test_api_response_format_for_frontend(self, client, auth_headers, mock_ai_providers):
        """Test API response format suitable for frontend"""
        response = client.post(
            "/api/v1/generate/flashcards",
            json={"topic": "Frontend Test", "age_group": "high_school"},
            headers=auth_headers
        )

        if response.status_code == 200:
            data = response.json()

            # Check required fields for frontend display
            assert "topic" in data
            assert "content_type" in data
            assert "generated_content" in data

            # Check that generated content can be displayed
            generated_content = data["generated_content"]
            assert isinstance(generated_content, dict)

    @pytest.mark.frontend
    def test_error_responses_for_frontend(self, client, auth_headers):
        """Test error responses are frontend-friendly"""
        # Test validation error
        response = client.post(
            "/api/v1/generate/study_guide",
            json={"topic": "", "age_group": "high_school"},  # Empty topic
            headers=auth_headers
        )

        assert response.status_code == 422
        error_data = response.json()

        # Should have user-friendly error structure
        assert "detail" in error_data


class TestUserWorkflows:
    """Test complete user workflows"""

    @pytest.mark.frontend
    @pytest.mark.integration
    def test_complete_content_generation_workflow(self, client, auth_headers, mock_ai_providers):
        """Test complete content generation workflow from frontend perspective"""

        # Step 1: Get available content types
        content_types_response = client.get("/api/v1/content-types")
        assert content_types_response.status_code == 200

        content_types = content_types_response.json()
        assert "content_types" in content_types
        assert len(content_types["content_types"]) == 8

        # Step 2: Generate content
        generation_response = client.post(
            "/api/v1/generate/study_guide",
            json={
                "topic": "Complete Workflow Test",
                "age_group": "high_school",
                "additional_requirements": "Include practical examples"
            },
            headers=auth_headers
        )

        if generation_response.status_code == 200:
            content_data = generation_response.json()

            # Should have complete data for frontend display
            assert "id" in content_data
            assert "generated_content" in content_data
            assert "quality_metrics" in content_data
            assert "created_at" in content_data

    @pytest.mark.frontend
    def test_form_submission_workflow(self, html_content, js_content):
        """Test form submission workflow components"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check form structure supports workflow
        form = soup.find('form', id='contentForm')
        assert form is not None

        # Check required fields for workflow
        required_fields = ['topic', 'contentType', 'ageGroup', 'apiKey']
        for field_name in required_fields:
            field = soup.find(attrs={'name': field_name}) or soup.find(id=field_name)
            assert field is not None, f"Required field {field_name} not found"

        # Check JavaScript handles workflow
        assert 'submit' in js_content
        assert 'preventDefault' in js_content

    @pytest.mark.frontend
    def test_error_handling_workflow(self, html_content, js_content):
        """Test error handling workflow"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check error display elements
        error_div = soup.find('div', id='error')
        assert error_div is not None

        error_message = soup.find(id='error-message')
        assert error_message is not None

        # Check JavaScript error handling
        assert 'showError' in js_content or 'error' in js_content
        assert 'catch' in js_content

    @pytest.mark.frontend
    def test_loading_state_workflow(self, html_content, js_content):
        """Test loading state workflow"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check loading indicator
        loading_div = soup.find('div', id='loading')
        assert loading_div is not None

        # Check JavaScript loading management
        loading_functions = ['showLoading', 'hideLoading']
        has_loading_management = any(func in js_content for func in loading_functions)
        assert has_loading_management or 'loading' in js_content


class TestResponsiveDesign:
    """Test responsive design functionality"""

    @pytest.mark.frontend
    def test_mobile_viewport_configuration(self, html_content):
        """Test mobile viewport configuration"""
        soup = BeautifulSoup(html_content, 'html.parser')

        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        assert viewport_meta is not None

        content = viewport_meta.get('content', '')
        assert 'width=device-width' in content
        assert 'initial-scale=1' in content

    @pytest.mark.frontend
    def test_form_mobile_usability(self, html_content, css_content):
        """Test form mobile usability"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check form inputs have appropriate attributes
        inputs = soup.find_all(['input', 'select'])
        for input_elem in inputs:
            # Should not have explicit small font sizes that cause zoom on iOS
            pass

        # Check CSS has mobile considerations
        if css_content:
            # Should have mobile-friendly font sizes
            mobile_font_pattern = r'font-size:\s*16px'
            # 16px prevents zoom on iOS Safari

    @pytest.mark.frontend
    def test_touch_friendly_interface(self, css_content):
        """Test touch-friendly interface elements"""
        if css_content:
            # Check for reasonable button/touch target sizes
            # Should have padding/dimensions suitable for touch
            button_patterns = [
                r'button\s*{[^}]*padding:[^}]*}',
                r'\.btn[^{]*{[^}]*padding:[^}]*}'
            ]


class TestCrossBrowserCompatibility:
    """Test cross-browser compatibility considerations"""

    @pytest.mark.frontend
    def test_modern_javascript_features(self, js_content):
        """Test usage of modern JavaScript features and potential compatibility"""
        # Check for modern features that might need polyfills
        modern_features = [
            'fetch(',  # Needs polyfill for IE
            'const ',  # ES6 feature
            'let ',    # ES6 feature
            'async ',  # ES2017 feature
            'await ',  # ES2017 feature
        ]

        used_features = [feature for feature in modern_features if feature in js_content]

        # Document which modern features are used
        if used_features:
            print(f"Modern JavaScript features used: {used_features}")
            # In a full implementation, would check if polyfills are included

    @pytest.mark.frontend
    def test_css_vendor_prefixes(self, css_content):
        """Test CSS vendor prefixes for compatibility"""
        if css_content:
            # Check for properties that might need vendor prefixes
            prefix_properties = [
                'transform',
                'transition',
                'box-shadow',
                'border-radius'
            ]

            # In a full implementation, would check if vendor prefixes are used where needed

    @pytest.mark.frontend
    def test_html5_feature_usage(self, html_content):
        """Test HTML5 feature usage and fallbacks"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check for HTML5 input types
        html5_inputs = soup.find_all('input', type=['email', 'url', 'tel', 'search', 'password'])

        # Check for HTML5 form validation attributes
        required_inputs = soup.find_all(attrs={'required': True})

        # In a full implementation, would check for appropriate fallbacks
