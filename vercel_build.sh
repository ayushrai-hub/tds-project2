#!/bin/bash

# Create necessary directories
mkdir -p static

# Copy frontend files to static directory
if [ -f frontend.html ]; then
  cp frontend.html static/
fi

# Copy other necessary files
for file in *.py; do
  cp "$file" "${file%.py}.pyc"
done
