# How to Pull Updates Safely - Step-by-Step Guide

Follow these steps to get the latest updates without breaking your app.

## ✅ Step 1: Check Your Current Status

Open your terminal/command prompt in your project folder and run:

```bash
# Navigate to your project folder
cd "C:\Ben\Business\Test Script Generator Project\BC-Projects"

# Check what branch you're on
git branch
```

You should see a `*` next to `claude/test-script-generator-012mQR9CF3ej16tYJH9oYwFo`

---

## ✅ Step 2: Save Any Local Changes (Optional)

If you've made any changes to files, save them first:

```bash
# See if you have any uncommitted changes
git status
```

**If you see modified files:**
```bash
# Save your changes temporarily
git stash
```

**If you see "nothing to commit, working tree clean":**
- Skip to Step 3 (you have no local changes to save)

---

## ✅ Step 3: Pull the Latest Updates

```bash
# Get the latest code from the server
git pull origin claude/test-script-generator-012mQR9CF3ej16tYJH9oYwFo
```

You should see messages like:
```
Updating e30dda2..553bef2
Fast-forward
 static/css/styles.css | 12 ++++++++----
 static/js/app.js      | 35 ++++++++++++++++++++---------------
 2 files changed, 29 insertions(+), 18 deletions(-)
```

---

## ✅ Step 4: Restore Your Changes (If You Stashed in Step 2)

**Only if you ran `git stash` in Step 2:**
```bash
# Restore your saved changes
git stash pop
```

**If you didn't stash anything, skip this step.**

---

## ✅ Step 5: Run the App

```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# You should see (venv) at the start of your prompt

# Run the app
python app.py
```

You should see:
```
⚠ pdfplumber not available (will use PyPDF2 only): No module named 'pdfplumber'
  This is normal on some Windows systems. PDF extraction will still work.
 * Running on http://127.0.0.1:5000
```

---

## ✅ Step 6: Test the Fix

1. Open your browser to `http://localhost:5000`
2. Upload your URS and template files
3. Click "Generate Test Script"
4. **Check the preview table** - The description and expected result textareas should now show all content and expand automatically!

---

## 🛡️ What If Something Goes Wrong?

### Problem: "error: Your local changes would be overwritten"

**Solution:**
```bash
# Save your changes first
git stash

# Then pull
git pull origin claude/test-script-generator-012mQR9CF3ej16tYJH9oYwFo

# Restore your changes
git stash pop
```

---

### Problem: "fatal: refusing to merge unrelated histories"

**Solution:**
```bash
# Force pull (only if you don't have important local changes!)
git reset --hard origin/claude/test-script-generator-012mQR9CF3ej16tYJH9oYwFo
```

⚠️ **Warning:** This will discard ALL local changes!

---

### Problem: App still doesn't work after pulling

**Solution:**
```bash
# Make sure you're on the right branch
git checkout claude/test-script-generator-012mQR9CF3ej16tYJH9oYwFo

# Pull again
git pull origin claude/test-script-generator-012mQR9CF3ej16tYJH9oYwFo

# Restart the app
python app.py
```

---

### Problem: "ModuleNotFoundError" errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements-minimal.txt

# Or install individually:
pip install Flask==3.0.0
pip install python-docx==1.1.0
pip install PyPDF2==3.0.1
pip install --upgrade anthropic
pip install python-dotenv==1.0.0
pip install Werkzeug==3.0.1
```

---

## 📋 Quick Command Summary (Copy and Paste)

For a fresh pull without any issues:

```bash
cd "C:\Ben\Business\Test Script Generator Project\BC-Projects"
git stash
git pull origin claude/test-script-generator-012mQR9CF3ej16tYJH9oYwFo
git stash pop
venv\Scripts\activate
python app.py
```

---

## ✨ What Changed in This Update

**Fix:** Textareas in the preview table now auto-resize to show all content

**Before:**
- Fixed height textareas
- Content was cut off
- Couldn't see full descriptions

**After:**
- Textareas automatically expand to fit content
- All text is visible
- Minimum height of 60px for readability
- Textareas grow as you type more content

---

## 💡 Pro Tips

1. **Always activate your virtual environment first:**
   ```bash
   venv\Scripts\activate
   ```

2. **Check if you have changes before pulling:**
   ```bash
   git status
   ```

3. **If unsure, stash first (it's safe):**
   ```bash
   git stash
   ```

4. **Keep your .env file safe** - it's in .gitignore and won't be affected by pulls

5. **The uploads/ folder is also safe** - it's gitignored too

---

## Need Help?

If you run into any issues:

1. Take a screenshot of the error
2. Run `git status` and copy the output
3. Run `pip list` and copy the output
4. Share these with me for troubleshooting

---

## Verify Everything Works

After pulling and running the app:

✅ Browser opens to `http://localhost:5000`
✅ You can upload files
✅ You can generate test script
✅ **Preview table shows all text in textareas**
✅ Textareas expand when you type
✅ You can edit all fields
✅ You can download the Word document

If all of these work, you're all set! 🎉
