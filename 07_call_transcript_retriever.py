import requests
import os
from dotenv import load_dotenv
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
OPENPHONE_API_KEY = os.getenv("OPENPHONE_API_KEY")

if not OPENPHONE_API_KEY:
    raise ValueError("OPENPHONE_API_KEY not found")

headers = {
    "Authorization": OPENPHONE_API_KEY,
}

with open("data/reference/phone_details.json", "r") as f:
    call_data = json.load(f)

for item in call_data:
    callid = item["callid"]
    try:
        response = requests.get(
            f"https://api.openphone.com/v1/call-transcripts/{callid}",
            headers=headers,
            timeout=10,
        )
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.text}")

        if response.status_code != 200:
            logger.error(f"Error status {response.status_code} for call {callid}")
            continue

        transcript_data = response.json()
        item["call_transcript"] = transcript_data

    except Exception as e:
        logger.error(f"Error processing call {callid}: {str(e)}")
        continue

with open("data/reference/phone_details.json", "w") as f:
    json.dump(call_data, f, indent=2)
