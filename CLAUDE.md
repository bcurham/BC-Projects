# CLAUDE.md - AI Assistant Guide for BC-Projects

## Repository Overview

**Repository Name:** BC-Projects
**Purpose:** A repository dedicated to pharmaceutical and medical device software validation automation, specifically focused on generating test scripts from User Requirements Specifications (URS) documents.

**Primary Use Case:** Automate the creation of GxP-compliant test documentation for FDA-regulated software systems.

---

## Repository Structure

```
BC-Projects/
├── README.md              # Repository description
├── master_prompt.md       # Core prompt for URS-to-test-script generation
├── master_prompt.txt      # Reserved for future use
└── CLAUDE.md             # This file - AI assistant guide
```

### File Descriptions

#### `master_prompt.md`
**Purpose:** Contains the master prompt template for Claude AI to parse URS documents and generate structured test scripts.

**Key Features:**
- Extracts individual requirements from URS documents
- Generates detailed test scripts in JSON format
- Outputs structured data compatible with Word/Google Docs templates
- Follows GxP compliance standards for pharmaceutical/medical device validation

**Output Format:**
```json
{
  "test_steps": [
    {
      "step_no": 1,
      "requirement_id": "REQ-001",
      "description": "Test step description",
      "expected_result": "Expected outcome"
    }
  ]
}
```

#### `master_prompt.txt`
**Status:** Currently empty - reserved for future plain text variations or alternative formats.

#### `README.md`
**Purpose:** Basic repository documentation for human readers.

---

## Development Workflows

### Git Branch Strategy

**Current Branch:** `claude/claude-md-mi5si5w3d52zzmcj-01UmKZx6jQn9kQYqkrN4itJ1`

**Branch Naming Convention:**
- Feature branches: `claude/claude-md-<session-id>`
- All Claude AI development occurs on designated feature branches
- Branch names must start with `claude/` prefix for proper authentication

**Important Git Rules:**
1. **ALWAYS** develop on the designated feature branch
2. **NEVER** push to main/master without explicit permission
3. Use `git push -u origin <branch-name>` for all pushes
4. Retry network failures up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

### Commit Message Guidelines

**Format:**
```
<type>: <concise description>

[optional body with detailed explanation]
```

**Types:**
- `feat`: New feature or prompt enhancement
- `fix`: Bug fix or correction
- `docs`: Documentation updates
- `refactor`: Code restructuring without functional changes
- `test`: Test-related changes
- `chore`: Maintenance tasks

**Examples:**
```
feat: Add acceptance criteria parsing to master prompt

docs: Update CLAUDE.md with workflow guidelines

fix: Correct JSON output format in test script template
```

---

## Key Conventions for AI Assistants

### 1. Domain-Specific Knowledge

This repository operates in a **highly regulated industry** (pharmaceutical/medical devices). AI assistants must:

- Use precise, professional language suitable for FDA/GxP compliance
- Maintain accuracy in all validation documentation
- Never summarize or merge test steps unless explicitly requested
- Preserve requirement order as it appears in source documents
- Follow 21 CFR Part 11 principles for electronic records

### 2. File Handling Rules

**When Modifying `master_prompt.md`:**
- ✅ **DO:** Preserve the core JSON structure
- ✅ **DO:** Maintain backward compatibility with existing URS parsers
- ✅ **DO:** Test any changes against sample URS text
- ❌ **DON'T:** Change the output format without documenting
- ❌ **DON'T:** Remove validation-critical fields

**When Creating New Files:**
- ✅ **DO:** Follow the existing naming conventions
- ✅ **DO:** Add documentation to this CLAUDE.md file
- ✅ **DO:** Update README.md if it affects end-users
- ❌ **DON'T:** Create files without clear purpose

### 3. Prompt Engineering Standards

When working with or modifying the master prompt:

1. **Clarity:** Instructions must be unambiguous
2. **Structure:** Use clear sections with headers
3. **Examples:** Always include input/output examples
4. **Constraints:** Explicitly state what NOT to do
5. **Format:** Specify exact output formats (JSON, Markdown, etc.)

### 4. Testing and Validation

Before committing changes to `master_prompt.md`:

1. Test with sample URS text
2. Validate JSON output structure
3. Verify requirement ID parsing
4. Check expected result clarity
5. Ensure GxP compliance language

---

## Common Tasks and Commands

### Analyzing URS Documents

**Task:** Parse a URS and generate test scripts

**Process:**
1. Read the master prompt: `master_prompt.md:1-123`
2. Apply the prompt to the provided URS text
3. Generate JSON output following the exact structure
4. Validate against the template requirements

### Updating the Master Prompt

**Before Changes:**
```bash
# Read current version
cat master_prompt.md

# Check git status
git status
```

**Making Changes:**
1. Read the file completely
2. Make targeted edits using the Edit tool
3. Test the changes
4. Commit with descriptive message

**After Changes:**
```bash
# Review changes
git diff

# Commit
git add master_prompt.md
git commit -m "feat: <description of change>"

# Push to feature branch
git push -u origin claude/claude-md-<session-id>
```

### Creating Documentation

**When Adding New Prompts or Tools:**
1. Create the file with clear naming
2. Add documentation section to this CLAUDE.md
3. Update README.md if user-facing
4. Commit all changes together

---

## Best Practices for AI Assistants

### Communication Style
- **Professional and precise** - This is regulated industry work
- **No emojis** unless explicitly requested
- **Concise responses** - Get to the point
- **Technical accuracy** over friendliness

### Code and Prompt Quality
- **Validate all JSON** output before presenting
- **Follow templates exactly** - Deviation can break automation
- **Preserve formatting** - Whitespace matters in structured documents
- **Test edge cases** - URS documents vary widely

### Error Handling
- **Never guess** requirement IDs - extract them accurately
- **Flag ambiguities** - Ask for clarification if URS text is unclear
- **Validate inputs** - Ensure URS text is provided before processing
- **Report issues** - If the prompt can't handle something, document why

---

## Regulatory and Compliance Notes

### GxP Compliance Requirements

This repository supports validation in GxP environments. AI assistants must understand:

- **Traceability:** Every requirement must trace to a test step
- **Completeness:** All requirements must be tested (no skipping)
- **Accuracy:** Test steps must precisely match requirements
- **Documentation:** Changes must be documented and justified

### 21 CFR Part 11 Awareness

While this repository doesn't directly handle electronic signatures, the output is used in Part 11 compliant systems:

- Maintain data integrity
- Ensure accurate and complete records
- Preserve audit trails through git history
- Never modify historical records inappropriately

---

## Future Development Areas

Based on the current repository structure, potential expansion areas include:

1. **Additional Prompts:**
   - Protocol generation from URS
   - Traceability matrix creation
   - Risk assessment automation

2. **Template Library:**
   - Word document templates
   - Google Docs templates
   - Excel validation templates

3. **Integration Scripts:**
   - Python scripts for URS parsing
   - Document conversion utilities
   - Template population automation

4. **Testing Framework:**
   - Sample URS documents
   - Expected output examples
   - Validation test suites

---

## Contact and Support

For questions or issues:
- Create an issue in the repository
- Contact the repository maintainer
- Review existing documentation in `master_prompt.md`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-19 | Initial CLAUDE.md creation with comprehensive documentation |

---

## Quick Reference

### Essential File Locations
- Master Prompt: `master_prompt.md:1-123`
- Repository Info: `README.md:1-2`

### Key Git Commands
```bash
# Check status
git status

# View changes
git diff

# Commit changes
git add .
git commit -m "type: description"

# Push to feature branch
git push -u origin claude/claude-md-<session-id>

# View commit history
git log --oneline
```

### Important Reminders
- ✅ Always work on feature branches
- ✅ Test JSON output validity
- ✅ Maintain GxP compliance language
- ✅ Document all changes
- ❌ Never modify main branch directly
- ❌ Never guess requirement IDs
- ❌ Never merge or summarize test steps without permission

---

*This document is maintained for AI assistants working with the BC-Projects repository. Last updated: 2025-11-19*
