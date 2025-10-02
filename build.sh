#!/usr/bin/env bash
# Render build script

set -o errexit  # exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip

# Force install pydantic-core with pre-built wheel first
echo "Installing pydantic-core with pre-built wheel..."
pip install --force-reinstall --no-deps pydantic-core==2.3.0

# Install other dependencies
echo "Installing other dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"