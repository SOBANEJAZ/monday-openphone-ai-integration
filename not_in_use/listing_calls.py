from dotenv import load_dotenv
import json
import requests
import os

# Load environment variables
load_dotenv()
OPENPHONE_API_KEY = os.getenv("OPENPHONE_API_KEY")


# Save All the Calls of the Phone Numbers to a JSON File

headers = {"Authorization": OPENPHONE_API_KEY}
params = {"phoneNumberId": "PN2efaBYSV", "participants": "+16124722781"}

response = requests.get("https://api.openphone.com/v1/calls", params=params, headers=headers).json()

with open("calls.json", "w") as f:
    json.dump(response, f, indent=4)

print("Calls data saved to calls.json")    
