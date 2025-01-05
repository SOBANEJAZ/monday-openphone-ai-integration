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
with open("initial_data/init.json", "r") as f:
    boards = json.load(f)

with open("initial_data/phone_details.json", "w") as f:
    for call in converted_data:
        for board in boards:
            if call["To"] == board["number"] or call["From"] == board["number"]:
                call["Board_id"] = board["Board_id"]
                call["Staff Member"] = board["Staff Member"]
    json.dump(converted_data, f, indent=4)            