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

