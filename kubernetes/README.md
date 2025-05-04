# A few small projects

The idea is to have some small self-contained examples to better understand the basic concepts.

## Even - Odd Predictor

Step 1: Containerize the application
```bash
docker build -t odd-even-app:v1 .
docker run -p 5000:5000 odd-even-app:v1
```
Test it in the browser: http://localhost:5000/predict?number=10

Step 2: Deploy to kubernetes
First make sure your local K8s cluster is running (e.g. `minikube start`)
Load the image to the cluster (e.g. `minikube image load odd-even-app:v1`)
Apply the deployment and service manifests:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```
Verify:
```bash
kubectl get pods
kubectl get deployment
kubectl get service
```
Test inside the cluster:
```bash
kubectl run tmp-curl --image=curlimages/curl -it --rm -- sh
curl http://odd-even-service/predict?number=7
```

Step 3: Expose externally and manage configuration
Make sure the `spec > type` is changed to `NodePort` (from `ClusterIP`) and apply the updated service
```bash
kubectl apply -f service.yaml`
minikube service odd-even-service --url # To find the access URL
```
Test accesing the URL from the browser or with curl (e.g. `http://127.0.0.1:52587/predict?number=7`).
Apply the ConfigMap:
```bash
kubectl apply -f configmap.yaml
```
Make sure to add the environment variable section to `deployment.yaml` and apply the updated deployment
```bash
kubectl apply -f deployment.yaml
```
Test the external URL again. The `message` field in the JSON response should now reflect the value from the ConfigMap

Step 4: Kubeflow
Install Kubeflow
```bash
export PIPELINE_VERSION=2.5.0
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=$PIPELINE_VERSION"
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```
Also make sure `kfp` is installed in your python environment - `pip install kfp==1.8.22`
 
 Compile and upload the pipeline
 ```bash
 python odd_even_pipeline.py
 ```

 Upload and run the pipeline
 ```bash
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
 ```
Open http://localhost:8080 in your browser. In the Kubeflow UI:
- Click on "Pipelines" in the sidebar
- Click "Upload pipeline"
- Select your `odd_even_pipeline.yaml` file
- Give it a name (e.g., "Odd-Even Predictor Pipeline")
- Click "Create"
To run the pipeline:
- Find your pipeline in the list
- Click on it
- Click "Create run"
- Configure any parameters if needed
- Click "Start"

Access the application
```bash
# Get the NodePort of your service
kubectl get svc odd-even-service -o jsonpath='{.spec.ports[0].nodePort}'

# If using minikube, get the URL
minikube service odd-even-service --url
```
Visit the URL in your browser with a parameter: http://<URL>/predict?number=42