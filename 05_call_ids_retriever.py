import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Get the API key from the environment
OPENPHONE_API_KEY = os.getenv("OPENPHONE_API_KEY")


headers = {
    "Authorization": OPENPHONE_API_KEY,
}

dir = "data/reference/phone_details.json"

with open(dir, "r") as f:
    phone_details = json.load(f)
for filename, item in enumerate(phone_details):
    if len(item) == 9:
        if item["Direction"] == "incoming":
            params = {
                "phoneNumberId": item["id"],
                "participants": item["From"],
            }
            response = requests.get("https://api.openphone.com/v1/calls", params=params, headers=headers).json()

            with open(f"data/call_logs/{filename}.json", "w") as f:
                f.write(json.dumps(response, indent=2))





with open(dir, "w") as f:
    f.write(json.dumps(phone_details, indent=4))

