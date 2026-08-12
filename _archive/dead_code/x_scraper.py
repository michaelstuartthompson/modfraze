import subprocess
import json

# Define the keyword you want to search for
query = "art"

# Number of posts
limit = 5

# Build the snscrape command (CLI)
cmd = [
    "snscrape",
    "--jsonl",
    f"twitter-search \"{query}\"",
    f"--max-results={limit}"
]

try:
    # Run the command and capture output
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    # Each line is a JSON tweet object
    for i, line in enumerate(result.stdout.splitlines(), start=1):
        tweet = json.loads(line)
        username = tweet.get("user", {}).get("username", "unknown")
        content = tweet.get("content", "")
        print(f"{i}. @{username} - {content}")

except subprocess.CalledProcessError as e:
    print("Error running snscrape CLI:")
    print(e.stderr)

