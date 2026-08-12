import os
from dotenv import load_dotenv
from openai import OpenAI

# Load keys from .env file
load_dotenv()

# Load API key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize client
client = OpenAI(api_key=api_key)

# Simple prompt
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say something uplifting."}]
)

# Show the response
print(response.choices[0].message.content)


