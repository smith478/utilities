from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
prompt = "Explain the concept of Occam's Razor and provide a simple, everyday example."
response = client.models.generate_content(
    model="gemini-2.5-pro-exp-03-25",  # or gemini-2.0-flash-thinking-exp
    contents=prompt
)

print("Response text:")
print(response.text)
print("Response full response:")
print(response)