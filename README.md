# RAG Application

A Retrieval-Augmented Generation (RAG) application built with Python, FastAPI, OpenAI, and ChromaDB. This application allows you to upload documents and query them using natural language through both a user-friendly Streamlit frontend and a REST API.

## Features

- **Document Upload**: Support for PDF, DOCX, and TXT files
- **Text Processing**: Intelligent text chunking and preprocessing
- **Vector Search**: ChromaDB for efficient document retrieval
- **AI Generation**: OpenAI GPT models for response generation
- **Streamlit Frontend**: User-friendly web interface for document management and querying
- **REST API**: FastAPI-based API with automatic documentation
- **Containerization**: Docker and docker-compose support
- **Kubernetes Ready**: Manifests for Azure Kubernetes Service deployment

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Docker (for containerized deployment)
- Kubernetes cluster (for K8s deployment)

### ⚡ Quick Start with Scripts

1. **Clone and start**:
   ```bash
   git clone <repository-url>
   cd agenticApps
   ./start.sh
   ```
   This script will:
   - Create environment file from template
   - Build and start both FastAPI backend and Streamlit frontend
   - Open the applications at:
     - Streamlit Frontend: http://localhost:8501
     - FastAPI Backend: http://localhost:8000

2. **Test the application**:
   ```bash
   python test_rag_app.py
   ```

### 🐍 Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd agenticApps
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key:
   # OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Upload sample documents** (optional):
   ```bash
   # Sample documents are already in the data/ directory
   ls data/
   ```

5. **Run the application**:
   ```bash
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the application**:
   - Streamlit Frontend: http://localhost:8501 (recommended for users)
   - FastAPI Backend: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### 🐳 Docker Deployment

1. **Using the start script** (recommended):
   ```bash
   ./start.sh
   ```

2. **Manual Docker setup**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   docker-compose up --build -d
   ```

3. **Access the applications**:
   - **Streamlit Frontend**: http://localhost:8501 (User Interface)
   - **FastAPI Backend**: http://localhost:8000 (API)
   - **API Documentation**: http://localhost:8000/docs

## 🎨 Streamlit Frontend

The application includes a beautiful, user-friendly Streamlit frontend that provides:

### Key Features:
- **📤 Document Upload Interface**: Drag-and-drop support for PDF, DOCX, and TXT files
- **💬 Interactive Query Interface**: Natural language questioning with AI responses
- **📊 Real-time System Monitoring**: API health, document statistics, and performance metrics
- **🔍 Advanced Search Options**: Configurable result limits and source citations
- **📜 Query History**: Track recent searches and results
- **🗑️ Document Management**: Clear documents with confirmation safety

### Interface Preview:
```
┌─────────────────────────────────────────────────────────────┐
│                📚 RAG Document Assistant                    │
├─────────────┬───────────────────────────────────────────────┤
│  🔧 System  │  ┌─────────────┬─────────────────────────┐   │
│    Status   │  │ 📤 Upload   │ 💬 Query Documents      │   │
│             │  │ Documents   │                         │   │
│  ✅ API     │  └─────────────┴─────────────────────────┘   │
│    Healthy  │                                               │
│             │  [Interactive Content Area]                  │
│  📊 5 Docs  │  • File upload with progress tracking        │
│    Uploaded │  • Natural language query input             │
│             │  • AI responses with source citations       │
│  🗑️ Clear   │  • Real-time performance metrics            │
│    Data     │                                               │
└─────────────┴───────────────────────────────────────────────┘
```

### Quick Start with Streamlit:
1. Run `./start.sh` to start both backend and frontend
2. Open http://localhost:8501 in your browser
3. Upload documents using the Upload tab
4. Ask questions using the Query tab
5. Get AI-powered answers with source citations

For detailed usage instructions, see [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md).

### ☸️ Kubernetes Deployment (Azure AKS)

1. **Using the deployment script** (recommended):
   ```bash
   # Ensure you're connected to your AKS cluster
   az aks get-credentials --resource-group ragAksCluster_group --name ragAksCluster
   
   # Deploy with script
   ./deploy-k8s.sh
   ```

2. **Manual Kubernetes setup**:
   ```bash
   # Encode your OpenAI API key
   echo -n "your-openai-api-key" | base64
   
   # Edit k8s/secret.yaml and add the encoded key
   # Edit k8s/deployment.yaml and update the container image registry
   
   # Deploy to Kubernetes
   kubectl apply -f k8s/
   
   # Get external IPs
   kubectl get services -l 'app in (rag-app,streamlit-frontend)'
   ```

3. **Access the deployed application**:
   - **Streamlit Frontend**: External LoadBalancer IP on port 80
   - **FastAPI Backend**: Available via Ingress at `/api` path
   - **API Documentation**: Available via Ingress at `/api/docs`

## Quick Demo

After starting the application, you can test it using either the Streamlit frontend or the API directly:

### Option 1: Using Streamlit Frontend (Recommended)

1. **Open the Streamlit interface**: http://localhost:8501
2. **Upload documents**: 
   - Go to "📤 Upload Documents" tab
   - Select files from the `data/` directory or upload your own
   - Click "📁 Upload All Files"
3. **Query documents**:
   - Switch to "💬 Query Documents" tab
   - Ask: "What are the main topics covered?"
   - Review AI response with source citations

### Option 2: Using API Directly

#### 1. Upload Sample Documents
```bash
# Upload the sample ML document
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@data/sample_ml_intro.txt"

# Upload the sample cloud computing document  
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@data/sample_cloud_computing.txt"
```

#### 2. Query the Documents
```bash
# Ask about machine learning
curl -X POST "http://localhost:8000/query" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is machine learning and what are its types?",
       "max_results": 5,
       "include_sources": true
     }'

# Ask about cloud computing
curl -X POST "http://localhost:8000/query" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are the benefits of cloud computing?",
       "max_results": 3,
       "include_sources": true
     }'
```

### 3. Check Statistics
```bash
curl -X GET "http://localhost:8000/documents/stats"
```

## API Endpoints

### Upload Document
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your-document.pdf"
```

### Query Documents
```bash
curl -X POST "http://localhost:8000/query" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is the main topic of the document?",
       "max_results": 5,
       "include_sources": true
     }'
```

### Get Document Statistics
```bash
curl -X GET "http://localhost:8000/documents/stats"
```

### Clear All Documents
```bash
curl -X DELETE "http://localhost:8000/documents"
```

## Configuration

The application can be configured through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (required) |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model for generation |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-ada-002` | OpenAI model for embeddings |
| `DEBUG` | `false` | Enable debug mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `CHUNK_SIZE` | `1000` | Text chunk size for processing |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `RETRIEVAL_K` | `5` | Number of documents to retrieve |
| `SIMILARITY_THRESHOLD` | `0.7` | Minimum similarity score |

## Supported File Types

- **PDF** (`.pdf`)
- **Microsoft Word** (`.docx`)
- **Plain Text** (`.txt`)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   OpenAI API    │    │   ChromaDB      │
│                 │    │                 │    │                 │
│ - Upload docs   │◄───┤ - Embeddings    │    │ - Vector store  │
│ - Query API     │    │ - Generation    │    │ - Similarity    │
│ - Health check  │    │                 │    │   search        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Development

### Project Structure
```
src/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── models/
│   └── schemas.py       # Pydantic models
├── services/
│   ├── document_service.py     # Document processing
│   ├── embedding_service.py    # OpenAI embeddings
│   ├── retrieval_service.py    # Vector database
│   └── generation_service.py   # Response generation
└── utils/
    └── text_processing.py      # Text utilities
```

## Testing

### Run Basic Tests
```bash
# Test application structure and basic functionality
python test_rag_app.py

# Test basic imports and syntax (no external dependencies)
python test_basic.py
```

### Manual Testing
1. **Start the application**:
   ```bash
   ./start.sh  # or docker-compose up
   ```

2. **Upload a document**:
   - Go to http://localhost:8000/docs
   - Use the `/upload` endpoint to upload a PDF, DOCX, or TXT file
   - Or use the sample documents in the `data/` directory

3. **Query the documents**:
   - Use the `/query` endpoint to ask questions
   - Check the response includes relevant sources

4. **Monitor health**:
   - Check http://localhost:8000/health for application status

## Monitoring and Logging

- Health check endpoint: `/health`
- Structured logging with configurable levels
- Docker health checks included
- Kubernetes liveness and readiness probes

## Security Considerations

- Non-root user in Docker container
- Environment-based configuration
- API key stored in Kubernetes secrets
- Resource limits in Kubernetes deployment

## Scaling

The application is designed to be scalable:

- Stateless design (vector DB persisted separately)
- Kubernetes horizontal pod autoscaling ready
- Load balancer support
- Persistent volume claims for data storage

## Troubleshooting

### Common Issues

1. **OpenAI API key not set**:
   - Ensure `OPENAI_API_KEY` is properly configured

2. **File upload fails**:
   - Check file size limits (default 10MB)
   - Verify supported file formats

3. **No relevant documents found**:
   - Lower `SIMILARITY_THRESHOLD` in configuration
   - Upload more relevant documents

4. **Memory issues**:
   - Adjust `CHUNK_SIZE` to smaller values
   - Increase container memory limits

## License

This project is licensed under the MIT License.