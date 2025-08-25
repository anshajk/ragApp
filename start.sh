#!/bin/bash

# RAG Application Startup Script

set -e

echo "🚀 Starting RAG Application Setup..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key!"
    echo "   OPENAI_API_KEY=your-api-key-here"
    echo ""
fi

# Check if OpenAI API key is set
if [ -f ".env" ]; then
    source .env
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
        echo "❌ OpenAI API key not set in .env file!"
        echo "   Please edit .env and set: OPENAI_API_KEY=your-actual-api-key"
        exit 1
    fi
fi

# Create data directory if it doesn't exist
mkdir -p data chroma_db

echo "✅ Environment setup complete!"
echo ""
echo "🐳 Starting application with Docker Compose..."
echo ""

# Start the application
docker compose up --build

echo ""
echo "🎉 RAG Application started successfully!"
echo ""
echo "🌐 Application Access:"
echo "   📱 Streamlit Frontend: http://localhost:8501"
echo "   📡 FastAPI Backend: http://localhost:8000"
echo "   📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "💡 Use the Streamlit interface for easy document upload and querying!"