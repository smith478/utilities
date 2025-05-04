import kfp
from kfp import dsl
from kfp.components import func_to_container_op

@func_to_container_op
def deploy_to_kubernetes(deployment_yaml: str, service_yaml: str, configmap_yaml: str):
    """Deploys the application to Kubernetes."""
    import subprocess
    import yaml
    import os
    
    # Print current directory and list files to help debug
    print(f"Current directory: {os.getcwd()}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"  - {f}")
    
    # Create temporary files if inputs are paths that don't exist
    # This handles the case where the pipeline passes file paths that don't exist in the container
    def ensure_file(file_path, default_content):
        if not os.path.exists(file_path):
            print(f"File {file_path} not found, creating temporary file with default content")
            with open(file_path, 'w') as f:
                f.write(default_content)
        return file_path
    
    # Default content for ConfigMap
    configmap_content = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: odd-even-config
data:
  GREETING_MESSAGE: "Kubeflow pipeline: The number is"
"""
    # Default content for deployment
    deployment_content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: odd-even-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: odd-even
  template:
    metadata:
      labels:
        app: odd-even
    spec:
      containers:
        - name: odd-even-app
          image: odd-even-app:v1
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
          env:
          - name: GREETING_MESSAGE
            valueFrom:
              configMapKeyRef:
                name: odd-even-config
                key: GREETING_MESSAGE
"""
    # Default content for service
    service_content = """
apiVersion: v1
kind: Service
metadata:
  name: odd-even-service
spec:
  selector:
    app: odd-even
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: NodePort
"""
    
    # Ensure files exist
    configmap_file = ensure_file(configmap_yaml, configmap_content)
    deployment_file = ensure_file(deployment_yaml, deployment_content)
    service_file = ensure_file(service_yaml, service_content)
    
    # Install kubectl if needed
    try:
        subprocess.run(["kubectl", "version", "--client"], check=True, capture_output=True)
        print("kubectl is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing kubectl...")
        subprocess.run([
            "curl", "-LO", 
            "https://dl.k8s.io/release/v1.26.0/bin/linux/amd64/kubectl"
        ], check=True)
        subprocess.run(["chmod", "+x", "./kubectl"], check=True)
        subprocess.run(["mv", "./kubectl", "/usr/local/bin/kubectl"], check=True)
    
    try:
        # Apply ConfigMap
        print("Applying ConfigMap...")
        subprocess.run(["kubectl", "apply", "-f", configmap_file], check=True)
        
        # Apply deployment and service
        print("Applying Deployment...")
        subprocess.run(["kubectl", "apply", "-f", deployment_file], check=True)
        print("Applying Service...")
        subprocess.run(["kubectl", "apply", "-f", service_file], check=True)
        
        # Check status
        print("Checking deployment status...")
        subprocess.run(["kubectl", "get", "deployments"], check=True)
        subprocess.run(["kubectl", "get", "services"], check=True)
        
        return "Deployment successful"
    except subprocess.CalledProcessError as e:
        print(f"Error in deployment: {e}")
        return f"Deployment failed: {str(e)}"

@dsl.pipeline(
    name="Odd-Even Predictor Pipeline",
    description="A pipeline to deploy the odd-even predictor application using existing Docker image."
)
def odd_even_pipeline():
    # Deploy to Kubernetes using existing image
    deploy_task = deploy_to_kubernetes(
        deployment_yaml="deployment.yaml",
        service_yaml="service.yaml",
        configmap_yaml="configmap.yaml"
    )

if __name__ == "__main__":
    # Compile the pipeline
    kfp.compiler.Compiler().compile(odd_even_pipeline, "odd_even_pipeline.yaml")