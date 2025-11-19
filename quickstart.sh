#!/bin/bash

# Quick Start Script for Automated Test Script Generator
# This script helps you set up and run the application quickly

set -e  # Exit on error

echo "=========================================="
echo "Automated Test Script Generator"
echo "Quick Start Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Setting up environment variables..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: You need to configure your .env file!"
    echo ""
    echo "Please edit .env and add your Anthropic API key:"
    echo "  ANTHROPIC_API_KEY=sk-ant-api03-..."
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
    echo ""
fi

# Verify API key is set
if ! grep -q "sk-ant-api03-" .env 2>/dev/null; then
    echo "⚠️  Warning: Anthropic API key may not be set in .env"
    echo "Make sure to add your API key before using the application."
    echo ""
fi

# Create sample files
if [ ! -f "sample_test_script_template.docx" ] || [ ! -f "sample_urs_document.docx" ]; then
    echo "Creating sample files for testing..."
    python create_sample_files.py
    echo ""
fi

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Starting the application..."
echo ""
echo "Once started, open your browser and go to:"
echo "  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

# Start the Flask application
python app.py
