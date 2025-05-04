import kfp
from kfp import dsl
from kfp.components import create_component_from_func
from kubernetes.client.models import V1Volume, V1VolumeMount, V1EmptyDirVolumeSource

# Define a function that will deploy our application
def deploy_odd_even_application(deployment_file: str, service_file: str):
    """Deploy the odd-even predictor application using provided manifest files."""
    import subprocess
    import os
    
    print(f"Current working directory: {os.getcwd()}")
    print("Files in directory:")
    print(subprocess.run(["ls", "-la"], capture_output=True, text=True).stdout)
    
    print(f"Content of deployment file ({deployment_file}):")
    with open(deployment_file, 'r') as f:
        print(f.read())
        
    print(f"Content of service file ({service_file}):")
    with open(service_file, 'r') as f:
        print(f.read())
    
    # Create ConfigMap
    configmap_content = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: odd-even-config
data:
  GREETING_MESSAGE: "Kubeflow Pipeline with Volume: The number is"
"""
    with open('configmap.yaml', 'w') as f:
        f.write(configmap_content)
    
    # Apply Kubernetes resources
    print("Applying ConfigMap...")
    subprocess.run(["kubectl", "apply", "-f", "configmap.yaml"], check=True)
    
    print("Applying Deployment...")
    subprocess.run(["kubectl", "apply", "-f", deployment_file], check=True)
    
    print("Applying Service...")
    subprocess.run(["kubectl", "apply", "-f", service_file], check=True)
    
    # Get service info
    print("Getting service information...")
    service_info = subprocess.run(
        ["kubectl", "get", "svc", "odd-even-service", "-o", "wide"],
        check=True, capture_output=True, text=True
    )
    print(service_info.stdout)
    
    # Check pods
    print("Checking pods...")
    pods_info = subprocess.run(
        ["kubectl", "get", "pods", "-l", "app=odd-even", "-o", "wide"],
        check=True, capture_output=True, text=True
    )
    print(pods_info.stdout)
    
    return "Deployment completed successfully!"

# Create a component
deploy_component = create_component_from_func(
    func=deploy_odd_even_application,
    base_image="bitnami/kubectl:latest",  # Image with kubectl pre-installed
    packages_to_install=[],  # No additional packages needed
)

# Define pipeline
@dsl.pipeline(
    name="Odd-Even Predictor Volume Pipeline",
    description="Pipeline deploying the odd-even predictor app using a volume for manifest files"
)
def odd_even_volume_pipeline():
    # Create a volume op to store our Kubernetes manifest files
    manifest_volume_op = dsl.VolumeOp(
        name="create-manifest-volume",
        resource_name="manifest-volume",
        size="1Gi",
        modes=dsl.VOLUME_MODE_RWO
    )
    
    # Create a container op to prepare the manifest files
    prepare_manifests_op = dsl.ContainerOp(
        name="prepare-manifests",
        image="alpine:3.14",
        command=["sh", "-c"],
        arguments=[
            """
            # Create deployment.yaml
            cat > /mnt/manifests/deployment.yaml << 'EOF'
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
EOF

            # Create service.yaml
            cat > /mnt/manifests/service.yaml << 'EOF'
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
EOF

            echo "Manifest files created successfully."
            ls -la /mnt/manifests/
            """
        ],
        pvolumes={"/mnt/manifests": manifest_volume_op.volume}
    )
    
    # Create a deploy op using our component
    deploy_op = deploy_component(
        deployment_file="/mnt/manifests/deployment.yaml",
        service_file="/mnt/manifests/service.yaml"
    ).add_pvolumes({"/mnt/manifests": manifest_volume_op.volume}).after(prepare_manifests_op)
    
    # Set resource limits
    deploy_op.set_cpu_request('100m')
    deploy_op.set_memory_request('256Mi')
    
    # Add annotations for better visibility in the UI
    deploy_op.add_pod_annotation("pipelines.kubeflow.org/execution_cache", "false")

# Compile the pipeline if run directly
if __name__ == "__main__":
    kfp.compiler.Compiler().compile(
        odd_even_volume_pipeline,
        "odd_even_volume_pipeline.yaml"
    )