import requests

url = "http://localhost:8000/transcribe"

with open('./audio_sample/sample.wav', 'rb') as file:
    files = {'file': file}
    response = requests.post(url, files=files)

if response.status_code == 200:
    print("Transcription successful:")
    print(response.json()["text"])
else:
    print(f"Error: {response.status_code}")
    print(response.text)