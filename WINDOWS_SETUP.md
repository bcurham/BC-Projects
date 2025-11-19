# Windows Setup Guide

This guide helps Windows users set up the Automated Test Script Generator, especially if you encounter cryptography/pdfplumber errors.

## Quick Fix for Cryptography Error

If you see this error when running `app.py`:
```
ImportError: DLL load failed while importing _rust: The specified procedure could not be found.
```

**Solution:** Use the minimal requirements file that skips pdfplumber:

```bash
# In your virtual environment:
pip install -r requirements-minimal.txt
```

The app will work perfectly with PyPDF2 for PDF extraction. You won't lose any functionality!

## Full Setup Instructions

### 1. Install Python

- Download Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
- **Important:** Check "Add Python to PATH" during installation
- Verify installation:
  ```bash
  python --version
  ```

### 2. Clone or Download the Project

```bash
cd C:\Your\Project\Folder
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

```bash
venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt.

### 5. Install Dependencies

**Option A: Try standard installation first**
```bash
pip install -r requirements.txt
```

**Option B: If Option A fails with cryptography error**
```bash
pip install -r requirements-minimal.txt
```

### 6. Configure Environment Variables

```bash
copy .env.example .env
```

Edit `.env` file with Notepad and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
FLASK_SECRET_KEY=your-random-secret-here
FLASK_ENV=development
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 7. Run the Application

```bash
python app.py
```

You should see:
```
⚠ pdfplumber not available (will use PyPDF2 only): ...
  This is normal on some Windows systems. PDF extraction will still work.
WARNING: ANTHROPIC_API_KEY not set in environment variables!  # Fix this in .env
 * Running on http://0.0.0.0:5000
```

### 8. Open Browser

Navigate to: `http://localhost:5000`

## Troubleshooting

### Error: "Python is not recognized"
- Python is not in your PATH
- Reinstall Python with "Add to PATH" option checked
- Or manually add Python to PATH in System Environment Variables

### Error: "No module named 'flask'"
- Virtual environment not activated
- Run: `venv\Scripts\activate`
- You should see `(venv)` in your prompt

### Error: "cryptography" or "pdfplumber" issues
- Use `requirements-minimal.txt` instead
- The app works perfectly without pdfplumber

### Error: Port 5000 already in use
- Another application is using port 5000
- Change the port in `app.py`:
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
  ```

### PDF extraction not working
- If you're using requirements-minimal.txt, PyPDF2 handles PDFs
- Some complex PDFs may not extract perfectly
- Try converting PDF to Word (.docx) format first

## Alternative: Full pdfplumber Support

If you really want pdfplumber (better PDF extraction), you need to fix the cryptography dependency:

### Option 1: Install Visual C++ Redistributables
1. Download [Microsoft Visual C++ 2015-2022 Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Install it
3. Restart your computer
4. Try `pip install -r requirements.txt` again

### Option 2: Upgrade pip and cryptography
```bash
pip install --upgrade pip
pip install --upgrade cryptography
pip install -r requirements.txt
```

### Option 3: Use Python 3.11
Some Windows systems work better with Python 3.11:
1. Install Python 3.11 from python.org
2. Create new virtual environment
3. Try installation again

## Still Having Issues?

1. Delete virtual environment:
   ```bash
   rmdir /s venv
   ```

2. Start fresh:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements-minimal.txt
   ```

3. The app will work fine without pdfplumber!

## Verification Test

To verify everything works:

```bash
python
```

```python
>>> import flask
>>> import anthropic
>>> import docx
>>> import PyPDF2
>>> print("All core dependencies loaded successfully!")
>>> exit()
```

If all imports work, you're ready to go!

## Performance Notes

- **PyPDF2 alone**: Works on all Windows systems, handles most PDFs
- **With pdfplumber**: Better extraction for complex PDFs, but requires cryptography
- **Recommendation**: Start with requirements-minimal.txt and only add pdfplumber if you need it

## Need Help?

If you still have issues after trying these solutions, create an issue on GitHub with:
- Your Python version: `python --version`
- Your Windows version
- Full error message
- Output of: `pip list`
