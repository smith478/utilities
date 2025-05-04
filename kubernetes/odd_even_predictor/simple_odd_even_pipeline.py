import kfp
from kfp import dsl
from kfp.components import create_component_from_func

# Define a function for our component
def deploy_odd_even_predictor():
    """Deploy the odd-even predictor application to Kubernetes."""
    import subprocess
    import os
    import time
    
    # Create the ConfigMap file
    configmap_content = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: odd-even-config
data:
  GREETING_MESSAGE: "Kubeflow Pipeline: The number is"
"""
    with open('generated-configmap.yaml', 'w') as f:
        f.write(configmap_content)
    
    # Create kubernetes resources
    try:
        print("Applying ConfigMap...")
        subprocess.run(["kubectl", "apply", "-f", "generated-configmap.yaml"], check=True)
        
        print("Applying Deployment...")
        subprocess.run(["kubectl", "apply", "-f", "deployment.yaml"], check=True)
        
        print("Applying Service...")
        subprocess.run(["kubectl", "apply", "-f", "service.yaml"], check=True)
        
        # Wait for deployment to be ready
        print("Waiting for deployment to be ready...")
        time.sleep(10)  # Give it some time to start
        
        # Get deployment status
        deployment_status = subprocess.run(
            ["kubectl", "rollout", "status", "deployment/odd-even-deployment", "--timeout=60s"],
            check=True, capture_output=True, text=True
        )
        print(deployment_status.stdout)
        
        # Get service information
        service_info = subprocess.run(
            ["kubectl", "get", "service", "odd-even-service", "-o", "wide"],
            check=True, capture_output=True, text=True
        )
        print(service_info.stdout)
        
        # Try to get NodePort
        try:
            node_port = subprocess.run(
                ["kubectl", "get", "service", "odd-even-service", "-o", "jsonpath='{.spec.ports[0].nodePort}'"],
                check=True, capture_output=True, text=True
            )
            print(f"NodePort: {node_port.stdout}")
        except:
            print("Couldn't get NodePort")
        
        return "Deployment completed successfully!"
    
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return f"Deployment failed: {e}"

# Create a Kubeflow component
deploy_component = create_component_from_func(
    func=deploy_odd_even_predictor,
    base_image="bitnami/kubectl:latest",  # Image with kubectl pre-installed
    packages_to_install=["kubernetes"]
)

# Define the pipeline
@dsl.pipeline(
    name="Simple Odd-Even Predictor Pipeline",
    description="Simple pipeline to deploy the odd-even predictor app"
)
def odd_even_simple_pipeline():
    # Deploy the application
    deploy_op = deploy_component()
    # Set resource limits to avoid throttling
    deploy_op.set_cpu_request('100m')
    deploy_op.set_memory_request('256Mi')

# Compile the pipeline
if __name__ == "__main__":
    kfp.compiler.Compiler().compile(
        pipeline_func=odd_even_simple_pipeline,
        package_path="odd_even_simple_pipeline.yaml"
    )