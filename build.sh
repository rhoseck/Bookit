#!/usr/bin/env bash
# Render build script

set -o errexit  # exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip

# Install dependencies with binary wheels only (avoid Rust compilation)
echo "Installing dependencies with binary wheels..."
pip install --only-binary=all -r requirements.txt

echo "Build completed successfully!"