#!/bin/bash
# Vercel Build Script
# Copies frontend files to public directory and installs backend dependencies

set -e

echo "🔨 Building VISIONZ for Vercel..."

# Copy frontend files to public/
echo "📁 Copying frontend files..."
cp -r visionz_fixed/frontend/* public/ 2>/dev/null || true

# Ensure directories exist
mkdir -p public/js
mkdir -p public/data

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd visionz_fixed/backend
pip install -r requirements.txt --quiet

echo "✅ Build complete!"
