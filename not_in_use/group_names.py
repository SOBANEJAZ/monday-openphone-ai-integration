import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()
api = os.getenv("MONDAY_API_KEY")


url = "https://api.monday.com/v2"

headers = {
    "Content-Type": "application/json",
    "Authorization": api,
}


query = """
query {
  boards (ids: 8139951792) {
    groups {
      title
      id
    }
  }
}
"""

payload = {"query": query}

response = requests.post(
    url, headers=headers, json=payload
)

# Step 5: Handle the response
if response.status_code == 200:
    data = response.json()
    # Extract and print the groups data
    boards = data.get("data", {}).get("boards", [])
    for board in boards:
        groups = board.get("groups", [])
        with open("group_names.json", "w") as f:
            json.dump(groups, f, indent=4)
        for group in groups:
            print(f"Title: {group['title']}, ID: {group['id']}")
            

else:
    # If something went wrong, print the error message
    print(f"Error: {response.status_code}")
    print(response.text)

