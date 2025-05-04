from kfp.components import create_component_from_func

def deploy_odd_even_app(namespace: str = "default"):
    """Deploys the odd-even predictor application to Kubernetes."""
    import subprocess
    import yaml
    import tempfile
    import os
    
    # Create ConfigMap
    configmap_yaml = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: odd-even-config
  namespace: {namespace}
data:
  GREETING_MESSAGE: "Configured message from Kubeflow: The number is"
    """.format(namespace=namespace)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(configmap_yaml)
        configmap_file = f.name
    
    # Create Deployment
    deployment_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: odd-even-deployment
  namespace: {namespace}
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
    """.format(namespace=namespace)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(deployment_yaml)
        deployment_file = f.name
    
    # Create Service
    service_yaml = """
apiVersion: v1
kind: Service
metadata:
  name: odd-even-service
  namespace: {namespace}
spec:
  selector:
    app: odd-even
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: NodePort
    """.format(namespace=namespace)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(service_yaml)
        service_file = f.name
    
    # Apply the resources
    try:
        subprocess.run(["kubectl", "apply", "-f", configmap_file], check=True)
        subprocess.run(["kubectl", "apply", "-f", deployment_file], check=True)
        subprocess.run(["kubectl", "apply", "-f", service_file], check=True)
        
        # Get service URL
        service_info = subprocess.run(
            ["kubectl", "get", "service", "odd-even-service", "-n", namespace, "-o", "jsonpath='{.spec.ports[0].nodePort}'"],
            check=True, capture_output=True, text=True
        )
        node_port = service_info.stdout.strip("'")
        
        # If using minikube, get the URL
        try:
            minikube_ip = subprocess.run(
                ["minikube", "ip"],
                check=True, capture_output=True, text=True
            )
            access_url = f"http://{minikube_ip.stdout.strip()}:{node_port}"
            print(f"Application deployed. Access it at: {access_url}")
        except:
            print(f"Application deployed. NodePort: {node_port}")
            
    finally:
        # Clean up temporary files
        os.unlink(configmap_file)
        os.unlink(deployment_file)
        os.unlink(service_file)
    
    return f"Deployment to namespace {namespace} complete"

# Create a KFP component
deploy_odd_even_component = create_component_from_func(
    func=deploy_odd_even_app,
    base_image="python:3.9",
    packages_to_install=["kubernetes"]
)