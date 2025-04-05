import requests

class OllamaClient:
    def __init__(self, base_url="http://host.docker.internal:11434"):
        self.base_url = base_url
        
    def generate(self, model, prompt, system="", stream=False):
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": stream
        }
        response = requests.post(url, json=payload)
        return response.json()