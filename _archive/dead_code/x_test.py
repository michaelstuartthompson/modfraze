import os
from dotenv import load_dotenv
from xdk import Client

# Load variables from .env
load_dotenv()

bearer_token = os.getenv("X_BEARER_TOKEN")

# Initialize the X API client
client = Client(bearer_token=bearer_token)

# Do a simple recent search
response = client.posts.search_recent(query="art", max_results=5)

# Print the tweet text
for page in response:
    if page.data:
        for post in page.data:
            print(post.text)
