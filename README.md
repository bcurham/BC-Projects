# Automated Test Script Generator

A web-based automation system that parses User Requirements Specification (URS) documents and automatically generates GxP-compliant test scripts for pharmaceutical and medical device software validation.

## Features

✨ **Simple 3-Step Workflow**: Upload → Generate → Download
📄 **Multi-format URS Support**: Upload URS documents in PDF, DOCX, or TXT format
🤖 **AI-Powered Extraction**: Claude AI intelligently extracts requirements and generates test steps
📋 **Table Preview**: See exactly how your Word document will look before downloading
✏️ **Inline Editing**: Click any cell to edit requirement IDs, descriptions, or expected results
📊 **Template-Based**: Automatically populates your existing Word document templates
✅ **GxP Compliance**: Generates test scripts suitable for FDA 21 CFR Part 11 and GxP validation
🎨 **Clean Interface**: Modern, intuitive web interface with real-time feedback
🔒 **Session Management**: Secure, isolated sessions for multiple users

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (HTML/CSS/JS)  │
└────────┬────────┘
         │
    HTTP REST API
         │
┌────────┴────────┐
│  Flask Backend  │
│                 │
│  ┌──────────┐   │
│  │ URS      │   │
│  │ Parser   │   │
│  └──────────┘   │
│                 │
│  ┌──────────┐   │
│  │ Claude   │   │
│  │ API      │   │
│  └──────────┘   │
│                 │
│  ┌──────────┐   │
│  │ Template │   │
│  │ Populator│   │
│  └──────────┘   │
└─────────────────┘
```

## Prerequisites

- Python 3.8 or higher
- Anthropic API key (Claude AI)
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd BC-Projects
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
ANTHROPIC_API_KEY=sk-ant-api03-...
FLASK_SECRET_KEY=your-random-secret-key-here
FLASK_ENV=development
```

To generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Verify Master Prompt

Ensure `master_prompt.md` exists in the root directory. This file contains the instructions for Claude AI to parse URS documents and generate test steps.

## Usage

### Starting the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Creating a Test Script Template

Your Word template should contain a table with the following columns:

| Step | Requirement # | Description | Expected Result | Pass/Fail | Initial | Date |
|------|---------------|-------------|-----------------|-----------|---------|------|

**Important Notes:**
- The table should be the first table in your Word document
- Column headers can be customized, but the order should remain the same
- The Pass/Fail, Initial, and Date columns will remain empty for manual completion
- Save the template as a `.docx` file

### Generating Test Scripts - Simple 3-Step Process

#### Step 1: Upload Files
1. **Open your browser** and navigate to `http://localhost:5000`
2. **Upload URS Document**: Click "Choose File" and select your URS (PDF, DOCX, or TXT)
3. **Upload Test Script Template**: Click "Choose File" and select your Word template (.docx)

#### Step 2: Generate & Review
1. **Click "Generate Test Script"** button
2. **Wait for AI processing** (typically 30-60 seconds)
   - The AI extracts all requirements from your URS
   - Test steps are automatically generated
   - The populated table preview appears

3. **Review the Table Preview**:
   - See exactly how your Word document will look
   - All 7 columns are displayed:
     - Step | Requirement # | Description | Expected Result | Pass/Fail | Initial | Date
   - The last 3 columns (Pass/Fail, Initial, Date) remain empty for manual completion

4. **Edit Any Cell** (optional):
   - Click on any Requirement ID, Description, or Expected Result
   - The cell becomes editable
   - Changes are saved automatically
   - Hover effects show which cells are editable

#### Step 3: Download
1. **Click "Download Word Document"** when satisfied with the preview
2. **The populated Word document downloads immediately**
3. **Open and use** the document for validation testing

#### Alternative: Start Over
- Click "← Start Over" at any time to upload different files

### After Download

1. Open the downloaded Word document
2. During actual testing, complete:
   - Pass/Fail column (mark as Pass or Fail for each test)
   - Initial column (tester's initials)
   - Date column (date of test execution)
3. Follow your organization's validation and approval procedures

## API Endpoints

### POST `/api/generate-preview`

Generate test steps from URS for preview and editing.

**Request:**
```
Content-Type: multipart/form-data

urs_file: <file>
template_file: <file>
```

**Response:**
```json
{
  "session_id": "uuid",
  "test_steps": [
    {
      "step_no": 1,
      "requirement_id": "REQ-001",
      "description": "User shall log in with valid credentials",
      "expected_result": "User is logged in and directed to dashboard"
    }
  ]
}
```

### POST `/api/generate-final`

Generate final Word document from edited test steps.

**Request:**
```
Content-Type: application/json

{
  "session_id": "uuid",
  "test_steps": [...]
}
```

**Response:**
- Success: Binary Word document (.docx)
- Error: JSON with error message

### POST `/api/preview`

*(Legacy endpoint)* Preview test steps without template file.

**Request:**
```
Content-Type: multipart/form-data

urs_file: <file>
```

**Response:**
```json
{
  "test_steps": [...]
}
```

## Project Structure

```
BC-Projects/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── master_prompt.md        # Claude AI prompt instructions
├── .env                    # Environment variables (not in git)
├── .env.example           # Example environment file
├── uploads/               # Temporary file storage (auto-created)
├── templates/
│   └── index.html         # Main web interface
├── static/
│   ├── css/
│   │   └── styles.css     # Application styles
│   └── js/
│       └── app.js         # Frontend logic
└── README.md              # This file
```

## Customization

### Modifying the Master Prompt

Edit `master_prompt.md` to customize how Claude AI parses requirements and generates test steps. The prompt should:

- Define the expected JSON output format
- Specify parsing rules for requirements
- Include examples of input/output
- Set the tone and style for test step descriptions

### Template Customization

The application supports flexible table structures. Modify `app.py` in the `populate_word_template()` function to adjust column mapping:

```python
# Current mapping (7 columns):
row_cells[0].text = str(step.get('step_no', ''))      # Step
row_cells[1].text = step.get('requirement_id', '')    # Requirement #
row_cells[2].text = step.get('description', '')       # Description
row_cells[3].text = step.get('expected_result', '')   # Expected Result
row_cells[4].text = ''                                # Pass/Fail
row_cells[5].text = ''                                # Initial
row_cells[6].text = ''                                # Date
```

## Troubleshooting

### Issue: "No text could be extracted from URS document"

**Solutions:**
- Ensure your PDF is text-based (not scanned images)
- Try converting PDF to Word format first
- Check if the document is password-protected
- Verify the file is not corrupted

### Issue: "Invalid response from AI: missing test_steps"

**Solutions:**
- Check your ANTHROPIC_API_KEY in `.env`
- Verify the URS document has clear, numbered requirements
- Review the `master_prompt.md` file for proper formatting
- Check API rate limits on your Anthropic account

### Issue: "No table found in template document"

**Solutions:**
- Ensure your template has at least one table
- The table should be the first table in the document
- Verify the template is saved as `.docx` format

### Issue: "Server error" or 500 responses

**Solutions:**
- Check the console/terminal for error messages
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure the `uploads/` directory is writable
- Check file size limits (max 16MB)

## Security Considerations

- **API Keys**: Never commit `.env` file to version control
- **File Upload**: Maximum file size is 16MB
- **Temporary Files**: Uploaded files are automatically deleted after processing
- **Input Validation**: All file types and sizes are validated before processing
- **HTTPS**: Use HTTPS in production environments
- **Authentication**: Add authentication for production deployment

## Best Practices

1. **Review All Generated Content**: Always manually review test scripts before use
2. **Maintain Templates**: Keep your Word templates organized and version-controlled
3. **Clear Requirements**: Ensure URS documents have clearly numbered requirements
4. **Acceptance Criteria**: Include acceptance criteria in your URS for better test step generation
5. **Backup**: Keep backups of original URS documents and templates

## Production Deployment

For production use:

1. **Set Environment to Production**:
   ```
   FLASK_ENV=production
   ```

2. **Use a Production Server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Enable HTTPS**: Use nginx or Apache as a reverse proxy with SSL

4. **Add Authentication**: Implement user authentication and authorization

5. **Configure Logging**: Set up proper logging for monitoring and debugging

6. **Database**: Consider adding a database to track generation history

## License

[Specify your license here]

## Support

For issues, questions, or contributions, please [create an issue](link-to-issues) in the repository.

## Compliance Notice

This tool generates test scripts for software validation in regulated industries. Users are responsible for:

- Reviewing all generated content for accuracy
- Ensuring compliance with applicable regulations (FDA 21 CFR Part 11, GxP, etc.)
- Maintaining proper documentation and audit trails
- Following their organization's validation procedures

The AI-generated content should be treated as a draft requiring subject matter expert review
