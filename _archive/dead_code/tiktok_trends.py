import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get your RapidAPI TikTok key
rapidapi_key = os.getenv("RAPIDAPI_TIKTOK_KEY")

# Define the TikTok API endpoint and headers
url = "https://tiktok-api23.p.rapidapi.com/api/music/posts"
querystring = {
    "musicId": "7224128604890990593",
    "count": "5",
    "cursor": "0"
}
headers = {
    "X-RapidAPI-Key": rapidapi_key,
    "X-RapidAPI-Host": "tiktok-api23.p.rapidapi.com"
}

# Make the request
response = requests.get(url, headers=headers, params=querystring)

# --- DEBUG (safe): show status + a small preview of the response ---
print("DEBUG status:", response.status_code)
print("DEBUG content-type:", response.headers.get("content-type"))

try:
    data = response.json()
    print("DEBUG top-level type:", type(data))
    if isinstance(data, dict):
        print("DEBUG top-level keys:", list(data.keys())[:30])
        # show common error fields if they exist
        for k in ("message", "msg", "error", "errors", "status", "statusCode", "code"):
            if k in data:
                print(f"DEBUG {k}:", data.get(k))
except Exception as e:
    print("DEBUG json parse failed:", e)
    text_preview = response.text[:800] if hasattr(response, "text") else str(response)[:800]
    print("DEBUG text preview:", text_preview)
    raise
# --- END DEBUG ---

# Handle and print the results
if response.status_code != 200:
    print("Error:", response.status_code, response.text[:300])
    raise SystemExit

posts = data.get("itemList", [])
print(f"Found {len(posts)} posts")

if not posts:
    raise SystemExit

for i, item in enumerate(posts, start=1):
    author = item.get("author", {}).get("uniqueId", "unknown")
    caption = item.get("desc", "[no description]")
    print(f"{i}. @{author} - {caption}")
