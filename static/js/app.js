// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const ursFile = document.getElementById('ursFile');
const templateFile = document.getElementById('templateFile');
const ursFileName = document.getElementById('ursFileName');
const templateFileName = document.getElementById('templateFileName');
const previewBtn = document.getElementById('previewBtn');
const generateBtn = document.getElementById('generateBtn');
const loadingSection = document.getElementById('loadingSection');
const loadingText = document.getElementById('loadingText');
const previewSection = document.getElementById('previewSection');
const previewContent = document.getElementById('previewContent');
const closePreview = document.getElementById('closePreview');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const successSection = document.getElementById('successSection');

// Update file names when files are selected
ursFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        ursFileName.textContent = e.target.files[0].name;
    } else {
        ursFileName.textContent = 'No file selected';
    }
    hideMessages();
});

templateFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        templateFileName.textContent = e.target.files[0].name;
    } else {
        templateFileName.textContent = 'No file selected';
    }
    hideMessages();
});

// Hide all message sections
function hideMessages() {
    errorSection.classList.add('hidden');
    successSection.classList.add('hidden');
    previewSection.classList.add('hidden');
}

// Show error message
function showError(message) {
    hideMessages();
    errorMessage.textContent = message;
    errorSection.classList.remove('hidden');
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Show success message
function showSuccess() {
    hideMessages();
    successSection.classList.remove('hidden');
    successSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Show loading state
function showLoading(message = 'Processing your documents...') {
    hideMessages();
    loadingText.textContent = message;
    loadingSection.classList.remove('hidden');
    generateBtn.disabled = true;
    previewBtn.disabled = true;
}

// Hide loading state
function hideLoading() {
    loadingSection.classList.add('hidden');
    generateBtn.disabled = false;
    previewBtn.disabled = false;
}

// Render preview of test steps
function renderPreview(testSteps) {
    if (!testSteps || testSteps.length === 0) {
        previewContent.innerHTML = '<p>No test steps generated.</p>';
        return;
    }

    let html = '<div class="test-steps-list">';

    testSteps.forEach(step => {
        html += `
            <div class="test-step">
                <div class="test-step-header">
                    <span class="step-no">Step ${step.step_no}</span>
                    <span class="req-id">${step.requirement_id}</span>
                </div>
                <div class="test-step-desc">
                    <strong>Description:</strong> ${escapeHtml(step.description)}
                </div>
                <div class="test-step-expected">
                    <strong>Expected Result:</strong> ${escapeHtml(step.expected_result)}
                </div>
            </div>
        `;
    });

    html += '</div>';
    previewContent.innerHTML = html;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Preview test steps
previewBtn.addEventListener('click', async () => {
    if (!ursFile.files[0]) {
        showError('Please select a URS document to preview.');
        return;
    }

    const formData = new FormData();
    formData.append('urs_file', ursFile.files[0]);

    showLoading('Analyzing URS document and generating test steps...');

    try {
        const response = await fetch('/api/preview', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        hideLoading();

        if (response.ok) {
            renderPreview(data.test_steps);
            previewSection.classList.remove('hidden');
            previewSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            showError(data.error || 'Failed to generate preview.');
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
});

// Close preview
closePreview.addEventListener('click', () => {
    previewSection.classList.add('hidden');
});

// Generate test script
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!ursFile.files[0] || !templateFile.files[0]) {
        showError('Please select both URS document and template file.');
        return;
    }

    const formData = new FormData();
    formData.append('urs_file', ursFile.files[0]);
    formData.append('template_file', templateFile.files[0]);

    showLoading('Generating your test script... This may take a minute.');

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            // Download the file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'generated_test_script.docx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            hideLoading();
            showSuccess();

            // Reset form
            uploadForm.reset();
            ursFileName.textContent = 'No file selected';
            templateFileName.textContent = 'No file selected';
        } else {
            const data = await response.json();
            hideLoading();
            showError(data.error || 'Failed to generate test script.');
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
});
