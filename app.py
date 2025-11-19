import os
import json
import uuid
from flask import Flask, request, jsonify, send_file, render_template, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import anthropic
from docx import Document
import PyPDF2
import pdfplumber
from io import BytesIO
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Anthropic client
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("WARNING: ANTHROPIC_API_KEY not set in environment variables!")
client = anthropic.Anthropic(api_key=api_key) if api_key else None

ALLOWED_URS_EXTENSIONS = {'pdf', 'docx', 'txt'}
ALLOWED_TEMPLATE_EXTENSIONS = {'docx'}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def extract_text_from_pdf(file_path):
    """Extract text from PDF file using pdfplumber for better accuracy"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"PDF has {len(pdf.pages)} pages")
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    print(f"Page {i+1}: extracted {len(page_text)} characters")
    except Exception as e:
        # Fallback to PyPDF2
        print(f"pdfplumber failed, trying PyPDF2: {e}")
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"PDF has {len(pdf_reader.pages)} pages")
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        print(f"Page {i+1}: extracted {len(page_text)} characters")
        except Exception as e2:
            print(f"PyPDF2 also failed: {e2}")
            raise ValueError(f"Unable to extract text from PDF. The file may be password-protected, corrupted, or contains only images. Error: {str(e2)}")

    if not text.strip():
        raise ValueError("PDF file appears to be empty or contains only images. Please ensure the PDF has extractable text.")

    return text


def extract_text_from_docx(file_path):
    """Extract text from Word document including paragraphs and tables"""
    try:
        doc = Document(file_path)
        text = ""

        # Extract from paragraphs
        paragraph_count = 0
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
                paragraph_count += 1

        print(f"Extracted {paragraph_count} paragraphs from Word document")

        # Extract from tables
        table_count = 0
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text += cell.text + "\n"
            table_count += 1

        print(f"Extracted text from {table_count} tables in Word document")

        if not text.strip():
            raise ValueError("Word document appears to be empty or contains no extractable text.")

        return text
    except Exception as e:
        print(f"Error extracting from Word document: {e}")
        raise ValueError(f"Unable to read Word document. The file may be corrupted or in an unsupported format. Error: {str(e)}")


def extract_text_from_txt(file_path):
    """Extract text from plain text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        if not text.strip():
            raise ValueError("Text file is empty.")

        print(f"Extracted {len(text)} characters from text file")
        return text
    except UnicodeDecodeError:
        # Try different encodings
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
            print(f"Extracted {len(text)} characters from text file using latin-1 encoding")
            return text
        except Exception as e:
            raise ValueError(f"Unable to read text file. The file encoding may not be supported. Error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unable to read text file: {str(e)}")


def extract_urs_text(file_path, filename):
    """Extract text from URS document based on file type"""
    print(f"Extracting text from: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'} bytes")

    ext = filename.rsplit('.', 1)[1].lower()

    if ext == 'pdf':
        text = extract_text_from_pdf(file_path)
    elif ext == 'docx':
        text = extract_text_from_docx(file_path)
    elif ext == 'txt':
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    print(f"Extracted text length: {len(text)} characters")
    print(f"First 200 chars: {text[:200] if text else 'EMPTY'}")

    return text


def load_master_prompt():
    """Load the master prompt from master_prompt.md"""
    try:
        with open('master_prompt.md', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        # Fallback to embedded prompt if file doesn't exist
        return """You are an expert in software validation for pharmaceutical and medical device industries.
Parse the URS document and extract all individual requirements.
Generate a detailed test script for each requirement in valid JSON format only.

Output structure:
{
  "test_steps": [
    {
      "step_no": 1,
      "requirement_id": "REQ-001",
      "description": "Requirement description",
      "expected_result": "Expected outcome"
    }
  ]
}

Rules:
- Each requirement becomes one test step
- Maintain order of requirements
- Treat sub-parts (1.1, 1.2) as separate steps
- Use clear, professional language for FDA/GxP compliance
- Output valid JSON only, no markdown or commentary"""


def generate_test_steps_with_claude(urs_text):
    """Use Claude API to parse URS and generate test steps"""
    master_prompt = load_master_prompt()

    # Construct the prompt
    prompt = f"""{master_prompt}

URS Text:
{urs_text}

Generate the JSON output with test_steps array now:"""

    # Call Claude API
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Extract the response
    response_text = message.content[0].text

    # Try to parse JSON from the response
    # Sometimes Claude might wrap it in markdown code blocks
    response_text = response_text.strip()

    # Remove markdown code blocks if present
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    if response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    # Parse JSON
    try:
        test_data = json.loads(response_text)
        return test_data
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Response: {response_text}")
        raise ValueError(f"Failed to parse JSON from Claude response: {e}")


def populate_word_template(template_path, test_steps):
    """Populate the Word template with test steps"""
    doc = Document(template_path)

    # Find the table in the document (assumes first table is the test script table)
    if len(doc.tables) == 0:
        raise ValueError("No table found in template document")

    table = doc.tables[0]

    # Verify table has correct headers (at least requirement columns)
    # Expected columns: Step | Requirement # | Description | Expected Result | Pass/Fail | Initial | Date

    # Add rows for each test step
    for step in test_steps:
        row_cells = table.add_row().cells

        # Populate cells (adjust indices based on your template structure)
        if len(row_cells) >= 7:
            row_cells[0].text = str(step.get('step_no', ''))
            row_cells[1].text = step.get('requirement_id', '')
            row_cells[2].text = step.get('description', '')
            row_cells[3].text = step.get('expected_result', '')
            # Leave Pass/Fail, Initial, Date empty for manual completion
            row_cells[4].text = ''
            row_cells[5].text = ''
            row_cells[6].text = ''
        elif len(row_cells) >= 4:
            # Minimal template
            row_cells[0].text = str(step.get('step_no', ''))
            row_cells[1].text = step.get('requirement_id', '')
            row_cells[2].text = step.get('description', '')
            row_cells[3].text = step.get('expected_result', '')

    return doc


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/generate-preview', methods=['POST'])
def generate_preview():
    """Generate test steps and return for preview/editing"""
    try:
        # Check if files are present
        if 'urs_file' not in request.files:
            return jsonify({'error': 'No URS file uploaded'}), 400

        if 'template_file' not in request.files:
            return jsonify({'error': 'No template file uploaded'}), 400

        urs_file = request.files['urs_file']
        template_file = request.files['template_file']

        # Validate files
        if urs_file.filename == '':
            return jsonify({'error': 'No URS file selected'}), 400

        if template_file.filename == '':
            return jsonify({'error': 'No template file selected'}), 400

        if not allowed_file(urs_file.filename, ALLOWED_URS_EXTENSIONS):
            return jsonify({'error': 'Invalid URS file type. Allowed: PDF, DOCX, TXT'}), 400

        if not allowed_file(template_file.filename, ALLOWED_TEMPLATE_EXTENSIONS):
            return jsonify({'error': 'Invalid template file type. Allowed: DOCX'}), 400

        # Save files temporarily with unique names
        session_id = str(uuid.uuid4())
        urs_filename = f"{session_id}_{secure_filename(urs_file.filename)}"
        template_filename = f"{session_id}_{secure_filename(template_file.filename)}"

        urs_path = os.path.join(app.config['UPLOAD_FOLDER'], urs_filename)
        template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_filename)

        urs_file.save(urs_path)
        template_file.save(template_path)

        print(f"Saved URS to: {urs_path}")
        print(f"Saved template to: {template_path}")

        # Step 1: Extract text from URS
        print("Extracting text from URS...")
        urs_text = extract_urs_text(urs_path, urs_file.filename)

        if not urs_text or not urs_text.strip():
            # Clean up files
            try:
                os.remove(urs_path)
                os.remove(template_path)
            except:
                pass
            return jsonify({'error': 'No text could be extracted from URS document. Please ensure it is a valid text-based document.'}), 400

        # Step 2: Generate test steps using Claude
        print("Generating test steps with Claude...")
        if not client:
            return jsonify({'error': 'Anthropic API key not configured. Please set ANTHROPIC_API_KEY in .env file.'}), 500

        test_data = generate_test_steps_with_claude(urs_text)

        if 'test_steps' not in test_data:
            return jsonify({'error': 'Invalid response from AI: missing test_steps'}), 500

        # Store template path in session for later download
        session['template_path'] = template_path
        session['session_id'] = session_id

        # Clean up URS file (we don't need it anymore)
        try:
            os.remove(urs_path)
        except:
            pass

        # Return test steps for preview/editing
        return jsonify({
            'test_steps': test_data['test_steps'],
            'session_id': session_id
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/generate-final', methods=['POST'])
def generate_final():
    """Generate final Word document from edited test steps"""
    try:
        data = request.get_json()

        if not data or 'test_steps' not in data:
            return jsonify({'error': 'No test steps provided'}), 400

        test_steps = data['test_steps']
        session_id = data.get('session_id')

        # Get template path from session or use default
        template_path = session.get('template_path')

        if not template_path or not os.path.exists(template_path):
            return jsonify({'error': 'Template file not found. Please upload files again.'}), 400

        # Populate Word template
        print("Populating Word template...")
        populated_doc = populate_word_template(template_path, test_steps)

        # Save to BytesIO
        output = BytesIO()
        populated_doc.save(output)
        output.seek(0)

        # Clean up template file
        try:
            os.remove(template_path)
            session.pop('template_path', None)
            session.pop('session_id', None)
        except:
            pass

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name='generated_test_script.docx'
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/preview', methods=['POST'])
def preview_test_steps():
    """Preview test steps without generating Word doc"""
    try:
        if 'urs_file' not in request.files:
            return jsonify({'error': 'No URS file uploaded'}), 400

        urs_file = request.files['urs_file']

        if urs_file.filename == '':
            return jsonify({'error': 'No URS file selected'}), 400

        if not allowed_file(urs_file.filename, ALLOWED_URS_EXTENSIONS):
            return jsonify({'error': 'Invalid URS file type. Allowed: PDF, DOCX, TXT'}), 400

        # Save file temporarily
        urs_filename = secure_filename(urs_file.filename)
        urs_path = os.path.join(app.config['UPLOAD_FOLDER'], urs_filename)
        urs_file.save(urs_path)

        # Extract text from URS
        urs_text = extract_urs_text(urs_path, urs_filename)

        if not urs_text.strip():
            return jsonify({'error': 'No text could be extracted from URS document'}), 400

        # Generate test steps using Claude
        test_data = generate_test_steps_with_claude(urs_text)

        # Clean up
        try:
            os.remove(urs_path)
        except:
            pass

        return jsonify(test_data)

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
