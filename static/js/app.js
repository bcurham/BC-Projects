// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const ursFile = document.getElementById('ursFile');
const templateFile = document.getElementById('templateFile');
const ursFileName = document.getElementById('ursFileName');
const templateFileName = document.getElementById('templateFileName');
const generateBtn = document.getElementById('generateBtn');
const loadingSection = document.getElementById('loadingSection');
const loadingText = document.getElementById('loadingText');
const previewSection = document.getElementById('previewSection');
const previewContent = document.getElementById('previewContent');
const closePreview = document.getElementById('closePreview');
const downloadBtn = document.getElementById('downloadBtn');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const successSection = document.getElementById('successSection');

// Store session data
let currentSessionId = null;
let currentTestSteps = [];

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
}

// Hide loading state
function hideLoading() {
    loadingSection.classList.add('hidden');
    generateBtn.disabled = false;
}

// Render editable preview of test steps in table format
function renderPreview(testSteps) {
    if (!testSteps || testSteps.length === 0) {
        previewContent.innerHTML = '<p>No test steps generated.</p>';
        return;
    }

    currentTestSteps = testSteps;

    // Create table structure matching the Word template
    let html = `
        <table class="test-script-table">
            <thead>
                <tr>
                    <th class="step-cell">Step</th>
                    <th class="req-id-cell">Requirement #</th>
                    <th class="description-cell">Description</th>
                    <th class="expected-cell">Expected Result</th>
                    <th class="status-cell">Pass/Fail</th>
                    <th class="status-cell">Initial</th>
                    <th class="status-cell">Date</th>
                </tr>
            </thead>
            <tbody>
    `;

    testSteps.forEach((step, index) => {
        html += `
            <tr data-index="${index}">
                <td class="step-cell">${step.step_no}</td>
                <td class="req-id-cell">
                    <input type="text"
                           class="table-cell-input"
                           data-field="requirement_id"
                           data-index="${index}"
                           value="${escapeHtml(step.requirement_id)}"
                           placeholder="REQ-ID">
                </td>
                <td class="description-cell">
                    <textarea class="table-cell-textarea auto-resize"
                              data-field="description"
                              data-index="${index}"
                              placeholder="Requirement description">${escapeHtml(step.description)}</textarea>
                </td>
                <td class="expected-cell">
                    <textarea class="table-cell-textarea auto-resize"
                              data-field="expected_result"
                              data-index="${index}"
                              placeholder="Expected result">${escapeHtml(step.expected_result)}</textarea>
                </td>
                <td class="status-cell">-</td>
                <td class="status-cell">-</td>
                <td class="status-cell">-</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
        <div class="table-info">
            ℹ️ Pass/Fail, Initial, and Date columns will remain empty in the downloaded document for completion during testing.
        </div>
    `;

    previewContent.innerHTML = html;

    // Add event listeners to update test steps when edited
    document.querySelectorAll('.table-cell-input, .table-cell-textarea').forEach(field => {
        // Update on change
        field.addEventListener('input', (e) => {
            const index = parseInt(e.target.dataset.index);
            const fieldName = e.target.dataset.field;
            currentTestSteps[index][fieldName] = e.target.value;

            // Auto-resize textareas as user types
            if (e.target.tagName === 'TEXTAREA') {
                autoResizeTextarea(e.target);
            }
        });
    });

    // Initial resize of all textareas to fit content
    // Use setTimeout to ensure DOM is fully rendered
    setTimeout(() => {
        document.querySelectorAll('.table-cell-textarea').forEach(textarea => {
            autoResizeTextarea(textarea);
        });
    }, 50);
}

// Auto-resize textarea to fit content
function autoResizeTextarea(textarea) {
    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';
    // Set to scrollHeight with minimum height of 60px
    textarea.style.height = Math.max(60, textarea.scrollHeight + 2) + 'px';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Generate preview
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!ursFile.files[0] || !templateFile.files[0]) {
        showError('Please select both URS document and template file.');
        return;
    }

    const formData = new FormData();
    formData.append('urs_file', ursFile.files[0]);
    formData.append('template_file', templateFile.files[0]);

    showLoading('Analyzing URS document and generating test steps... This may take a minute.');

    try {
        const response = await fetch('/api/generate-preview', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        hideLoading();

        if (response.ok) {
            currentSessionId = data.session_id;
            renderPreview(data.test_steps);
            previewSection.classList.remove('hidden');
            previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

            // Hide upload form
            document.querySelector('.upload-section').style.display = 'none';
        } else {
            showError(data.error || 'Failed to generate preview.');
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
});

// Close preview and reset
closePreview.addEventListener('click', () => {
    previewSection.classList.add('hidden');
    document.querySelector('.upload-section').style.display = 'block';
    currentSessionId = null;
    currentTestSteps = [];
    uploadForm.reset();
    ursFileName.textContent = 'No file selected';
    templateFileName.textContent = 'No file selected';
});

// Download final Word document
downloadBtn.addEventListener('click', async () => {
    if (!currentSessionId || currentTestSteps.length === 0) {
        showError('No test steps available. Please generate preview first.');
        return;
    }

    showLoading('Generating your Word document...');

    try {
        const response = await fetch('/api/generate-final', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                test_steps: currentTestSteps,
                session_id: currentSessionId
            })
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

            // Reset everything
            setTimeout(() => {
                previewSection.classList.add('hidden');
                document.querySelector('.upload-section').style.display = 'block';
                currentSessionId = null;
                currentTestSteps = [];
                uploadForm.reset();
                ursFileName.textContent = 'No file selected';
                templateFileName.textContent = 'No file selected';
            }, 2000);
        } else {
            const data = await response.json();
            hideLoading();
            showError(data.error || 'Failed to generate Word document.');
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
});
