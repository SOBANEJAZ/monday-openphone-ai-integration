from dotenv import load_dotenv
import json
import requests
import os

# Load environment variables
load_dotenv()
OPENPHONE_API_KEY = os.getenv("OPENPHONE_API_KEY")


# List of all phone numbers and their corresponding ids
headers = {"Authorization": OPENPHONE_API_KEY}
phone_numbers = requests.get(
    "https://api.openphone.com/v1/phone-numbers", headers=headers
).json()

with open("phone_numbers.json", "w") as f:
    json.dump(phone_numbers, f, indent=4)

print("Phone numbers data saved to phone_numbers.json")


