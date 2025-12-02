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

// Project naming variables
let projectName = '';
let projectDescription = '';

// Generate preview - show modal first to get project name
uploadForm.addEventListener('submit', (e) => {
    e.preventDefault();

    if (!ursFile.files[0] || !templateFile.files[0]) {
        showError('Please select both URS document and template file.');
        return;
    }

    // Show modal to get project name
    const modal = document.getElementById('projectNameModal');
    modal.classList.remove('hidden');

    // Auto-suggest project name from URS filename
    const suggestedName = ursFile.files[0].name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, ' ');
    document.getElementById('projectName').value = suggestedName;
    document.getElementById('projectDescription').value = '';

    // Focus on project name input
    setTimeout(() => {
        document.getElementById('projectName').focus();
        document.getElementById('projectName').select();
    }, 100);
});

// Handle project name form submission
document.getElementById('projectNameForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    projectName = document.getElementById('projectName').value.trim();
    projectDescription = document.getElementById('projectDescription').value.trim();

    if (!projectName) {
        alert('Please enter a project name');
        return;
    }

    // Close modal
    closeProjectModal();

    // Now proceed with file upload
    await generateTestScript();
});

// Function to actually generate the test script
async function generateTestScript() {
    const formData = new FormData();
    formData.append('urs_file', ursFile.files[0]);
    formData.append('template_file', templateFile.files[0]);
    formData.append('project_name', projectName);
    formData.append('project_description', projectDescription);

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
}

// Close project modal
function closeProjectModal() {
    document.getElementById('projectNameModal').classList.add('hidden');
}

// Close modal when clicking outside
document.getElementById('projectNameModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'projectNameModal') {
        closeProjectModal();
    }
});

// Close preview and reset
closePreview.addEventListener('click', () => {
    previewSection.classList.add('hidden');
    document.querySelector('.upload-section').style.display = 'block';

    // Hide enhanced features section
    const enhancedFeaturesSection = document.getElementById('enhancedFeaturesSection');
    if (enhancedFeaturesSection) {
        enhancedFeaturesSection.classList.add('hidden');
    }

    // Reset session data
    currentSessionId = null;
    currentTestSteps = [];
    currentUrsText = null;

    // Reset form
    uploadForm.reset();
    ursFileName.textContent = 'No file selected';
    templateFileName.textContent = 'No file selected';

    // Hide any result sections
    const qualityResults = document.getElementById('qualityResults');
    const changeResults = document.getElementById('changeResults');
    if (qualityResults) qualityResults.classList.add('hidden');
    if (changeResults) changeResults.classList.add('hidden');
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

            // Show enhanced features section after successful download
            const enhancedFeaturesSection = document.getElementById('enhancedFeaturesSection');
            if (enhancedFeaturesSection) {
                enhancedFeaturesSection.classList.remove('hidden');
                enhancedFeaturesSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }

            // Don't reset immediately - keep data for enhanced features
            // Reset everything
            // setTimeout(() => {
            //     previewSection.classList.add('hidden');
            //     document.querySelector('.upload-section').style.display = 'block';
            //     currentSessionId = null;
            //     currentTestSteps = [];
            //     uploadForm.reset();
            //     ursFileName.textContent = 'No file selected';
            //     templateFileName.textContent = 'No file selected';
            // }, 2000);
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

// ═══════════════════════════════════════════════════════════════════════════════
// ENHANCED VALIDATION FEATURES
// ═══════════════════════════════════════════════════════════════════════════════

// Additional session data for enhanced features
let currentUrsText = null;

// Tab switching functionality
document.addEventListener('DOMContentLoaded', () => {
    const featureTabs = document.querySelectorAll('.feature-tab');
    const tabContents = document.querySelectorAll('.tab-content');

    featureTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;

            // Remove active class from all tabs and contents
            featureTabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            const targetContent = document.getElementById(targetTab + 'Tab');
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });

    // Enhanced feature buttons
    setupEnhancedFeatureButtons();
});

// Setup all enhanced feature button event listeners
function setupEnhancedFeatureButtons() {
    // RTM Excel
    const rtmExcelBtn = document.getElementById('generateRTMExcel');
    if (rtmExcelBtn) {
        rtmExcelBtn.addEventListener('click', async () => {
            await generateRTM('excel');
        });
    }

    // RTM Word
    const rtmWordBtn = document.getElementById('generateRTMWord');
    if (rtmWordBtn) {
        rtmWordBtn.addEventListener('click', async () => {
            await generateRTM('word');
        });
    }

    // Validation Plan
    const vmpBtn = document.getElementById('generateVMP');
    if (vmpBtn) {
        vmpBtn.addEventListener('click', async () => {
            await generateValidationDoc('plan');
        });
    }

    // Validation Summary Report
    const vsrBtn = document.getElementById('generateVSR');
    if (vsrBtn) {
        vsrBtn.addEventListener('click', async () => {
            await generateValidationDoc('summary');
        });
    }

    // Quality Check
    const qualityBtn = document.getElementById('runQualityCheck');
    if (qualityBtn) {
        qualityBtn.addEventListener('click', async () => {
            await runQualityCheck();
        });
    }

    // Change Analysis
    const changeBtn = document.getElementById('runChangeAnalysis');
    if (changeBtn) {
        changeBtn.addEventListener('click', async () => {
            await runChangeAnalysis();
        });
    }

    // Audit Package
    const auditBtn = document.getElementById('exportAuditPackage');
    if (auditBtn) {
        auditBtn.addEventListener('click', async () => {
            await exportAuditPackage();
        });
    }
}

// Generate Requirements Traceability Matrix
async function generateRTM(format) {
    if (!currentTestSteps || currentTestSteps.length === 0) {
        showError('No test steps available. Please generate a test script first.');
        return;
    }

    const endpoint = format === 'excel' ? '/api/generate-rtm-excel' : '/api/generate-rtm-word';
    const filename = format === 'excel' ? 'RTM_Traceability_Matrix.xlsx' : 'RTM_Traceability_Matrix.docx';

    showLoading(`Generating RTM (${format.toUpperCase()})...`);

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                test_steps: currentTestSteps
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            downloadFile(blob, filename);
            hideLoading();
            showSuccess();
        } else {
            const data = await response.json();
            hideLoading();
            showError(data.error || `Failed to generate RTM (${format}).`);
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
}

// Generate Validation Documentation (VMP or VSR)
async function generateValidationDoc(docType) {
    if (!currentTestSteps || currentTestSteps.length === 0) {
        showError('No test steps available. Please generate a test script first.');
        return;
    }

    const endpoint = docType === 'plan' ? '/api/generate-validation-plan' : '/api/generate-validation-summary';
    const filename = docType === 'plan' ? 'Validation_Master_Plan.docx' : 'Validation_Summary_Report.docx';
    const docName = docType === 'plan' ? 'Validation Master Plan' : 'Validation Summary Report';

    showLoading(`Generating ${docName}...`);

    try {
        const response = await fetch(endpoint, {
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
            const blob = await response.blob();
            downloadFile(blob, filename);
            hideLoading();
            showSuccess();
        } else {
            const data = await response.json();
            hideLoading();
            showError(data.error || `Failed to generate ${docName}.`);
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
}

// Run Quality Check
async function runQualityCheck() {
    if (!currentSessionId) {
        showError('No URS document available. Please generate a test script first.');
        return;
    }

    showLoading('Analyzing requirement quality with AI...');

    try {
        const response = await fetch('/api/check-quality', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId
            })
        });

        const data = await response.json();
        hideLoading();

        if (response.ok) {
            renderQualityResults(data);
        } else {
            showError(data.error || 'Failed to run quality check.');
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
}

// Render quality check results
function renderQualityResults(data) {
    const resultsDiv = document.getElementById('qualityResults');
    if (!resultsDiv) return;

    let scoreClass = 'score-good';
    if (data.overall_score < 70) scoreClass = 'score-poor';
    else if (data.overall_score < 85) scoreClass = 'score-fair';

    let html = `
        <h4>Quality Analysis Results</h4>
        <div class="quality-score ${scoreClass}">
            Overall Quality Score: ${data.overall_score}%
        </div>
        <p><strong>Analysis Summary:</strong> ${data.summary}</p>
    `;

    if (data.issues && data.issues.length > 0) {
        html += '<h4>Issues Found:</h4>';
        data.issues.forEach(issue => {
            const severityClass = `severity-${issue.severity.toLowerCase()}`;
            html += `
                <div class="quality-issue">
                    <div class="issue-header">
                        <span class="issue-category">${issue.category}</span>
                        <span class="issue-severity ${severityClass}">${issue.severity}</span>
                    </div>
                    <p><strong>Issue:</strong> ${issue.description}</p>
                    <p><strong>Suggestion:</strong> ${issue.suggestion}</p>
                    ${issue.affected_requirements ? `<p><strong>Affected:</strong> ${issue.affected_requirements.join(', ')}</p>` : ''}
                </div>
            `;
        });
    } else {
        html += '<p style="color: green; font-weight: 600;">✓ No significant quality issues found!</p>';
    }

    resultsDiv.innerHTML = html;
    resultsDiv.classList.remove('hidden');
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Run Change Analysis
async function runChangeAnalysis() {
    if (!currentSessionId) {
        showError('No URS document available. Please generate a test script first.');
        return;
    }

    showLoading('Analyzing changes from previous version...');

    try {
        const response = await fetch('/api/analyze-changes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                test_steps: currentTestSteps,
                session_id: currentSessionId
            })
        });

        const data = await response.json();
        hideLoading();

        if (response.ok) {
            renderChangeResults(data);
        } else {
            showError(data.error || 'Failed to analyze changes.');
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
}

// Render change analysis results
function renderChangeResults(data) {
    const resultsDiv = document.getElementById('changeResults');
    if (!resultsDiv) return;

    let html = `
        <h4>Change Analysis Results</h4>
    `;

    if (data.is_first_baseline) {
        html += `
            <div class="change-summary">
                <p style="color: var(--primary-color); font-weight: 600;">
                    ℹ️ This is the first version. A baseline has been saved for future comparisons.
                </p>
            </div>
        `;
    } else {
        const impactClass = data.impact_level === 'HIGH' ? 'impact-high' :
                          data.impact_level === 'MEDIUM' ? 'impact-medium' : 'impact-low';

        html += `
            <div class="change-summary">
                <div class="change-stat">
                    <strong>Impact Level:</strong>
                    <span class="impact-badge ${impactClass}">${data.impact_level}</span>
                </div>
                <div class="change-stat">
                    <strong>Requirements Added:</strong>
                    <span>${data.summary.added}</span>
                </div>
                <div class="change-stat">
                    <strong>Requirements Removed:</strong>
                    <span>${data.summary.removed}</span>
                </div>
                <div class="change-stat">
                    <strong>Requirements Modified:</strong>
                    <span>${data.summary.modified}</span>
                </div>
                <div class="change-stat">
                    <strong>Requirements Unchanged:</strong>
                    <span>${data.summary.unchanged}</span>
                </div>
            </div>

            <h4>Impact Analysis:</h4>
            <p><strong>Tests to Add:</strong> ${data.impact.tests_to_add}</p>
            <p><strong>Tests to Update:</strong> ${data.impact.tests_to_update}</p>
            <p><strong>Tests to Reuse:</strong> ${data.impact.tests_to_reuse}</p>
            <p><strong>Recommendation:</strong> ${data.recommendations}</p>
        `;

        if (data.changes && data.changes.length > 0) {
            html += '<h4>Detailed Changes:</h4>';
            data.changes.forEach(change => {
                const changeColor = change.type === 'added' ? 'green' :
                                  change.type === 'removed' ? 'red' : 'orange';
                html += `
                    <div class="quality-issue" style="border-left-color: ${changeColor};">
                        <p><strong>${change.type.toUpperCase()}:</strong> ${change.requirement_id}</p>
                        <p>${change.description}</p>
                    </div>
                `;
            });
        }
    }

    resultsDiv.innerHTML = html;
    resultsDiv.classList.remove('hidden');
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Export Complete Audit Package
async function exportAuditPackage() {
    if (!currentTestSteps || currentTestSteps.length === 0 || !currentSessionId) {
        showError('No test script available. Please generate a test script first.');
        return;
    }

    showLoading('Generating complete audit package... This may take a minute.');

    try {
        const response = await fetch('/api/export-audit-package', {
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
            const blob = await response.blob();
            const timestamp = new Date().toISOString().split('T')[0];
            downloadFile(blob, `Audit_Package_${timestamp}.zip`);
            hideLoading();
            showSuccess();
        } else {
            const data = await response.json();
            hideLoading();
            showError(data.error || 'Failed to generate audit package.');
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
}

// Helper function to download files
function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
