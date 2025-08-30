#!/bin/bash

# Kubernetes Deployment Script for Minikube (Local Development)

set -e

echo "🏠 Deploying RAG Application to Minikube..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found! Please install kubectl first."
    exit 1
fi

# Check if minikube is available
if ! command -v minikube &> /dev/null; then
    echo "❌ minikube not found! Please install minikube first."
    echo "   Visit: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "🚀 Starting Minikube..."
    minikube start
    echo ""
fi

echo "📋 Current cluster context:"
kubectl config current-context
echo ""

# Set docker environment to use minikube's docker daemon
echo "🐳 Setting up Docker environment for Minikube..."
eval $(minikube docker-env)
echo ""

# Build Docker images locally in Minikube
echo "🔨 Building Docker images..."
if [ -f "Dockerfile" ]; then
    echo "Building backend image..."
    docker build -t rag-app:latest .
else
    echo "❌ Dockerfile not found! Please ensure you're in the project root directory."
    exit 1
fi

if [ -f "Dockerfile.streamlit" ]; then
    echo "Building frontend image..."
    docker build -f Dockerfile.streamlit -t rag-streamlit:latest .
else
    echo "❌ Dockerfile.streamlit not found! Please ensure you're in the project root directory."
    exit 1
fi

echo ""

# Prompt for OpenAI API key if not provided
if [ -z "$OPENAI_API_KEY" ]; then
    echo "🔑 Please enter your OpenAI API key:"
    read -s OPENAI_API_KEY
    echo ""
fi

# Encode the API key for Kubernetes secret
ENCODED_API_KEY=$(echo -n "$OPENAI_API_KEY" | base64)

# Update the secret file
echo "🔐 Creating Kubernetes secret..."
sed -i.bak "s/OPENAI_API_KEY: \"\"/OPENAI_API_KEY: \"$ENCODED_API_KEY\"/" k8s/minikube/secret.yaml

# Apply Kubernetes manifests
echo "🚀 Deploying to Minikube..."
kubectl apply -f k8s/minikube/

echo ""
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/rag-app
kubectl wait --for=condition=available --timeout=300s deployment/streamlit-frontend

echo ""
echo "📊 Deployment status:"
kubectl get pods,services -l 'app in (rag-app,streamlit-frontend)'

echo ""
echo "🎉 RAG Application deployed successfully to Minikube!"
echo ""
echo "🌍 Application Access:"

# Get minikube IP
MINIKUBE_IP=$(minikube ip)

echo "   📱 Streamlit Frontend: http://$MINIKUBE_IP:30080"
echo "   📡 FastAPI Backend: http://$MINIKUBE_IP:30800"
echo "   📚 API Documentation: http://$MINIKUBE_IP:30800/docs"

echo ""
echo "🚀 Quick access commands:"
echo "   minikube service streamlit-frontend-service    # Open frontend in browser"
echo "   minikube service rag-app-nodeport-service      # Open backend API"
echo ""
echo "🔧 Useful commands:"
echo "   kubectl logs -l app=rag-app -f                 # View backend logs"
echo "   kubectl logs -l app=streamlit-frontend -f      # View frontend logs"
echo "   kubectl get pods                               # Check pod status"
echo "   minikube dashboard                             # Open Kubernetes dashboard"
echo "   minikube stop                                  # Stop Minikube"

# Restore original secret file
mv k8s/minikube/secret.yaml.bak k8s/minikube/secret.yaml