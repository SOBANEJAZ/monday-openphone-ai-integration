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
    columns {
      id
      title
    }		
  }
}
"""

payload = {"query": query}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    # Save response to a JSON file
    with open("monday_response.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    print("Response saved to monday_response.json")
else:
    print("Failed to retrieve data. Status code:", response.status_code)
