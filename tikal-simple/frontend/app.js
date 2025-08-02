/**
 * Tikal Simple Frontend - Vanilla JS, No Framework
 * Total: ~150 lines (vs 9000+ files in original)
 */

// Check for saved API key on load
window.onload = function() {
    const savedKey = localStorage.getItem('apiKey');
    if (savedKey) {
        document.getElementById('apiKey').value = savedKey;
        document.getElementById('keyStatus').textContent = '✓ Saved';
        document.getElementById('keyStatus').className = 'success';
    }
};

// Save API key to localStorage
function saveApiKey() {
    const apiKey = document.getElementById('apiKey').value;
    if (apiKey) {
        localStorage.setItem('apiKey', apiKey);
        document.getElementById('keyStatus').textContent = '✓ Saved';
        document.getElementById('keyStatus').className = 'success';
    } else {
        document.getElementById('keyStatus').textContent = '✗ Required';
        document.getElementById('keyStatus').className = 'error';
    }
}

// Generate content
async function generateContent(event) {
    event.preventDefault();
    
    const apiKey = localStorage.getItem('apiKey');
    if (!apiKey) {
        showError('Please set your API key first');
        return;
    }
    
    // Get form values
    const topic = document.getElementById('topic').value;
    const contentType = document.getElementById('contentType').value;
    
    // Show loading state
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('error').classList.add('hidden');
    document.getElementById('output').classList.add('hidden');
    document.getElementById('generateBtn').disabled = true;
    
    try {
        // Make API call
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey
            },
            body: JSON.stringify({
                topic: topic,
                content_type: contentType
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display content
        document.getElementById('content').textContent = data.content;
        document.getElementById('output').classList.remove('hidden');
        
    } catch (error) {
        showError(error.message);
    } finally {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('generateBtn').disabled = false;
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = `Error: ${message}`;
    errorDiv.classList.remove('hidden');
}

// Copy content to clipboard
function copyContent() {
    const content = document.getElementById('content').textContent;
    navigator.clipboard.writeText(content).then(() => {
        alert('Content copied to clipboard!');
    });
}

// Download content as text file
function downloadContent() {
    const content = document.getElementById('content').textContent;
    const topic = document.getElementById('topic').value;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${topic.replace(/\s+/g, '_')}_content.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// Load stats
async function loadStats() {
    const apiKey = localStorage.getItem('apiKey');
    if (!apiKey) {
        showError('Please set your API key first');
        return;
    }
    
    try {
        const response = await fetch('/api/stats', {
            headers: {
                'X-API-Key': apiKey
            }
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const stats = await response.json();
        
        // Display stats
        document.getElementById('statsDisplay').innerHTML = `
            <p>Total Generations: <strong>${stats.total_generations}</strong></p>
            <p>Active Users: <strong>${stats.active_users}</strong></p>
            <p>Uptime: <strong>${stats.uptime_hours} hours</strong></p>
            <p>Last Generation: <strong>${new Date(stats.last_generation).toLocaleString()}</strong></p>
        `;
        
    } catch (error) {
        document.getElementById('statsDisplay').innerHTML = `<p class="error">Failed to load stats</p>`;
    }
}

// That's it! Entire frontend in ~150 lines
// No React, no TypeScript, no build process, no complexity