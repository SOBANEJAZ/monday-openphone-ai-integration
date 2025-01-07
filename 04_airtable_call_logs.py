import json
import requests
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

# Initialize the Airtable API
api = Api(os.getenv("AIRTABLE_API_KEY"))
table = api.table("appYvU5Req8gKzr7A", "tblUjWsTBe299fVF9")

# Get all the records from the Airtable
table = table.all()

import json
from datetime import datetime


def convert_json(data):

    converted_data = []
    for call in data:
        from_number = call["fields"].get("From")
        to_number = call["fields"].get("To")
        direction = call["fields"].get("Direction")
        transcriptions = call["fields"].get("Transcript")

        start_time = call["fields"].get("Start Time")
        if start_time:
            start_time = datetime.strptime(
                start_time, "%Y-%m-%dT%H:%M:%S.%fZ"
            ).strftime("%H:%M:%S")
        else:
            start_time = None

        end_time = call["fields"].get("End Time")
        if "T" in end_time:
            end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                "%H:%M:%S"
            )
        else:
            end_time = datetime.strptime(end_time, "%a, %d %b %Y %H:%M:%S %z").strftime(
                "%H:%M:%S"
            )

        converted_call = {
            "Direction": direction,
            "Board_id": "",
            "Staff Member": "",
            "From": from_number,
            "To": to_number,
            "Start Time": start_time,
            "End Time": end_time,
            "Transcript": transcriptions
        }
        converted_data.append(converted_call)

    return converted_data


converted_data = convert_json(table)
# Load additional JSON data
with open("data/reference/init.json", "r") as f:
    boards = json.load(f)

with open("data/reference/phone_details.json", "w") as f:
    for call in converted_data:
        for board in boards:
            if call["To"] == board["number"] or call["From"] == board["number"]:
                call["Board_id"] = board["Board_id"]
                call["Staff Member"] = board["Staff Member"]
    json.dump(converted_data, f, indent=4)


import json

# Load the first JSON file
with open("data/reference/init.json", "r") as f:
    first_data = json.load(f)

# Load the second JSON file
with open("data/reference/phone_details.json", "r") as f:
    second_data = json.load(f)

# Create a mapping from "number" to "id"
number_to_id = {item["number"]: item["id"] for item in first_data}

# Iterate through each item in the second JSON and add "id" if "To" matches
for item in second_data:
    to_number = item.get("To", "")
    if to_number in number_to_id:
        item["id"] = number_to_id[to_number]

# Save the modified second JSON to a new file
with open("data/reference/phone_details.json", "w") as f:
    json.dump(second_data, f, indent=4)

# Optional: Print the modified data
print(json.dumps(second_data, indent=4))
