#!/bin/bash

# Create api directory if it doesn't exist
mkdir -p api

# Copy main Python files to api directory
cp main.py api/
cp gemini.py api/
cp llm_parser.py api/
cp task_engine.py api/

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, uvicorn; print(f'FastAPI version: {fastapi.__version__}')"
