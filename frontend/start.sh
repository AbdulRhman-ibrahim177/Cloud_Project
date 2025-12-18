#!/bin/bash
# Quick start script for the frontend

echo "🚀 Starting Cloud Project Frontend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your settings!"
fi

# Apply migrations
echo "🔄 Applying database migrations..."
python manage.py migrate

# Run development server
echo ""
echo "✨ Starting development server..."
echo "🌐 Frontend available at: http://localhost:8000"
echo ""

python manage.py runserver
