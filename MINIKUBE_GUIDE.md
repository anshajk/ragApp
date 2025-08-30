# Minikube Deployment Guide

This guide provides detailed instructions for deploying the RAG Application locally using Minikube.

## Prerequisites

### 1. Install Required Tools

```bash
# Install Minikube
# Visit: https://minikube.sigs.k8s.io/docs/start/
# For example, on macOS:
brew install minikube

# Install kubectl
# Visit: https://kubernetes.io/docs/tasks/tools/install-kubectl/
# For example, on macOS:
brew install kubectl

# Install Docker (if not already installed)
# Visit: https://docs.docker.com/get-docker/
```

### 2. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --memory=4096 --cpus=2

# Verify Minikube is running
minikube status
```

## Deployment

### Quick Deployment

The simplest way to deploy is using the provided script:

```bash
# Ensure you're in the project root directory
cd agenticApps

# Deploy to Minikube (will prompt for OpenAI API key)
./deploy-minikube.sh
```

### Manual Deployment

If you prefer manual deployment:

```bash
# 1. Set up Docker environment
eval $(minikube docker-env)

# 2. Build images locally
docker build -t rag-app:latest .
docker build -f Dockerfile.streamlit -t rag-streamlit:latest .

# 3. Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# 4. Update the secret
ENCODED_API_KEY=$(echo -n "$OPENAI_API_KEY" | base64)
sed -i.bak "s/OPENAI_API_KEY: \"\"/OPENAI_API_KEY: \"$ENCODED_API_KEY\"/" k8s/minikube/secret.yaml

# 5. Deploy to Kubernetes
kubectl apply -f k8s/minikube/

# 6. Wait for deployments
kubectl wait --for=condition=available --timeout=300s deployment/rag-app
kubectl wait --for=condition=available --timeout=300s deployment/streamlit-frontend

# 7. Restore original secret file
mv k8s/minikube/secret.yaml.bak k8s/minikube/secret.yaml
```

## Access Applications

### Using Minikube Service Commands (Recommended)

```bash
# Open Streamlit frontend in browser
minikube service streamlit-frontend-service

# Open FastAPI backend in browser  
minikube service rag-app-nodeport-service
```

### Using Direct URLs

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Access applications
echo "Streamlit Frontend: http://$MINIKUBE_IP:30080"
echo "FastAPI Backend: http://$MINIKUBE_IP:30800"
echo "API Documentation: http://$MINIKUBE_IP:30800/docs"
```

## Monitoring and Troubleshooting

### Check Deployment Status

```bash
# View all pods and services
kubectl get pods,services -l 'app in (rag-app,streamlit-frontend)'

# Check pod logs
kubectl logs -l app=rag-app -f              # Backend logs
kubectl logs -l app=streamlit-frontend -f   # Frontend logs

# Describe pods for troubleshooting
kubectl describe pods -l app=rag-app
kubectl describe pods -l app=streamlit-frontend
```

### Kubernetes Dashboard

```bash
# Open Kubernetes dashboard
minikube dashboard
```

### Common Issues

1. **Images not found**: Ensure you've run `eval $(minikube docker-env)` before building images
2. **Services not accessible**: Check that Minikube is running with `minikube status`
3. **Pods not starting**: Check logs with `kubectl logs` and ensure OpenAI API key is set
4. **Resource issues**: Increase Minikube memory/CPU: `minikube start --memory=8192 --cpus=4`

## Cleanup

### Remove Deployment

```bash
# Delete all resources
kubectl delete -f k8s/minikube/

# Or delete individual components
kubectl delete deployment rag-app streamlit-frontend
kubectl delete service rag-app-service streamlit-frontend-service rag-app-nodeport-service
kubectl delete configmap rag-app-config
kubectl delete secret rag-app-secrets
kubectl delete pvc chroma-pvc data-pvc
```

### Stop Minikube

```bash
# Stop Minikube cluster
minikube stop

# Delete Minikube cluster (if you want to start fresh)
minikube delete
```

## Development Workflow

### Updating Application Code

When you make changes to the application:

```bash
# 1. Set Docker environment
eval $(minikube docker-env)

# 2. Rebuild images
docker build -t rag-app:latest .
docker build -f Dockerfile.streamlit -t rag-streamlit:latest .

# 3. Restart deployments to pick up new images
kubectl rollout restart deployment/rag-app
kubectl rollout restart deployment/streamlit-frontend

# 4. Wait for rollout to complete
kubectl rollout status deployment/rag-app
kubectl rollout status deployment/streamlit-frontend
```

### Testing Changes

```bash
# Run integration tests
python test_minikube_integration.py

# Test basic functionality
python test_rag_app.py
```

## Differences from Cloud Deployment

The Minikube deployment differs from the Azure AKS deployment in the following ways:

- **Service Types**: Uses NodePort instead of LoadBalancer
- **Image Handling**: Uses local images with `imagePullPolicy: Never`
- **Resource Limits**: Lower resource requirements for local development
- **Storage**: Uses Minikube's default storage class
- **Replicas**: Single replica for most components to conserve resources
- **Access**: Direct access via NodePort rather than cloud load balancers