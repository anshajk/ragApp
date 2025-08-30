#!/bin/bash

# Kubernetes Deployment Script for Azure AKS

set -e

echo "☸️  Deploying RAG Application to Azure Kubernetes Service..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found! Please install kubectl first."
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Not connected to a Kubernetes cluster!"
    echo "   Please configure kubectl to connect to your AKS cluster:"
    echo "   az aks get-credentials --resource-group myResourceGroup --name myAKSCluster"
    exit 1
fi

echo "📋 Current cluster context:"
kubectl config current-context
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
sed -i "s/OPENAI_API_KEY: \"\"/OPENAI_API_KEY: \"$ENCODED_API_KEY\"/" k8s/secret.yaml

# Apply Kubernetes manifests
echo "🚀 Deploying to Kubernetes..."
kubectl apply -f k8s/

echo ""
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/rag-app
kubectl wait --for=condition=available --timeout=300s deployment/streamlit-frontend

echo ""
echo "📊 Deployment status:"
kubectl get pods,services,ingress -l 'app in (rag-app,streamlit-frontend)'

echo ""
echo "🌐 Getting external IP addresses..."
FRONTEND_IP=""
while [ -z "$FRONTEND_IP" ]; do
    echo "Waiting for Streamlit frontend external IP..."
    FRONTEND_IP=$(kubectl get service streamlit-frontend-service --template="{{range .status.loadBalancer.ingress}}{{.ip}}{{end}}")
    [ -z "$FRONTEND_IP" ] && sleep 10
done

echo ""
echo "🎉 RAG Application deployed successfully!"
echo ""
echo "🌍 Application Access:"
echo "   📱 Streamlit Frontend: http://$FRONTEND_IP"
echo "   📡 FastAPI Backend: http://$FRONTEND_IP/api (via Ingress)"
echo "   📚 API Documentation: http://$FRONTEND_IP/api/docs (via Ingress)"

echo ""
echo "🔧 Useful commands:"
echo "   kubectl logs -l app=rag-app -f              # View backend logs"
echo "   kubectl logs -l app=streamlit-frontend -f   # View frontend logs"
echo "   kubectl get pods                            # Check pod status"
echo "   kubectl describe services                   # Service details"