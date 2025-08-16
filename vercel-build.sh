#!/bin/bash

# Update pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install specific versions of dependencies
pip install fastapi==0.116.1 uvicorn==0.35.0 python-multipart==0.0.20 python-dotenv==1.0.0 aiofiles==24.1.0

# Install additional required packages
pip install numpy==2.2.6 pandas==2.3.1 openai==1.99.1 google-generativeai==0.8.5 pydantic==2.11.7

# Verify installation
python -c "import fastapi, uvicorn; print(f'FastAPI version: {fastapi.__version__}')"
