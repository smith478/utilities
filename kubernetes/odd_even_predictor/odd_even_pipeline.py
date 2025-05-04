import kfp
from kfp import dsl
from kfp.components import func_to_container_op
from kubernetes.client.models import V1EnvVar

@func_to_container_op
def build_image(image_name: str, tag: str, dockerfile_path: str, context_path: str):
    """Builds a Docker image using kaniko."""
    import subprocess
    
    full_image_name = f"{image_name}:{tag}"
    subprocess.run([
        "kaniko",
        "--dockerfile", dockerfile_path,
        "--context", context_path,
        "--destination", full_image_name
    ], check=True)
    
    return full_image_name

@func_to_container_op
def deploy_to_kubernetes(image_name: str, deployment_yaml: str, service_yaml: str, configmap_yaml: str):
    """Deploys the application to Kubernetes."""
    import subprocess
    import yaml
    
    # Apply ConfigMap
    subprocess.run(["kubectl", "apply", "-f", configmap_yaml], check=True)
    
    # Modify the deployment YAML to use the built image
    with open(deployment_yaml, 'r') as f:
        deployment = yaml.safe_load(f)
    
    deployment['spec']['template']['spec']['containers'][0]['image'] = image_name
    
    # Write the modified deployment back
    with open('modified_deployment.yaml', 'w') as f:
        yaml.dump(deployment, f)
    
    # Apply the deployment and service
    subprocess.run(["kubectl", "apply", "-f", "modified_deployment.yaml"], check=True)
    subprocess.run(["kubectl", "apply", "-f", service_yaml], check=True)
    
    return "Deployment successful"

@dsl.pipeline(
    name="Odd-Even Predictor Pipeline",
    description="A pipeline to build and deploy the odd-even predictor application."
)
def odd_even_pipeline():
    # Define pipeline parameters
    image_name = "odd-even-app"
    tag = "v1"
    
    # Build the Docker image
    build_task = build_image(
        image_name=image_name,
        tag=tag,
        dockerfile_path="Dockerfile",
        context_path="."
    )
    
    # Deploy to Kubernetes
    deploy_task = deploy_to_kubernetes(
        image_name=f"{image_name}:{tag}",
        deployment_yaml="deployment.yaml",
        service_yaml="service.yaml",
        configmap_yaml="configmap.yaml"
    )
    
    # Set dependencies
    deploy_task.after(build_task)

if __name__ == "__main__":
    # Compile the pipeline
    kfp.compiler.Compiler().compile(odd_even_pipeline, "odd_even_pipeline.yaml")