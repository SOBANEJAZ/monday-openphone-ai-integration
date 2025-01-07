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


# params = {
#     "phoneNumberId": "PNApxJhnBC",
#     "participants": "+19522345483",
# }

# response = requests.get("https://api.openphone.com/v1/calls", params=params, headers=headers).json()

# with open("responses.json", "w") as f:
#     f.write(json.dumps(response, indent=2))
