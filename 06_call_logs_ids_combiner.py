import json
import os
from datetime import datetime
import glob


def process_json_files(main_json_path, call_logs_dir):
    # Read main JSON file
    with open(main_json_path, "r") as f:
        main_data = json.load(f)

    # Process each entry in main JSON
    for index, main_entry in enumerate(main_data):
        json_file_path = os.path.join(call_logs_dir, f"{index}.json")

        # Check if corresponding JSON file exists
        if not os.path.exists(json_file_path):
            continue

        # Read the corresponding JSON file
        with open(json_file_path, "r") as f:
            index_data = json.load(f)

        # Get main entry start time
        main_start_time = main_entry.get("Start Time")

        # Look through each item in the index file's data
        for item in index_data.get("data", []):
            # Get created time from index file
            created_at = item.get("createdAt")

            # Compare timestamps
            if main_start_time == created_at:
                # If times match, add the phoneNumberId to main entry
                main_entry["callid"] = item.get("id")
                break

    # Write updated data back to main JSON file
    with open(main_json_path, "w") as f:
        json.dump(main_data, f, indent=2)

    return main_data


process_json_files("data/reference/phone_details.json", "data/call_logs")


import json


def filter_items(data):
    """Filters items in the JSON data based on length."""
    filtered_items = []
    for item in data:
        if len(item) == 10:
            filtered_items.append(item)
    return filtered_items


# Load JSON data
with open("data/reference/phone_details.json", "r") as f:
    data = json.load(f)

# Filter items
filtered_data = filter_items(data)

# Update JSON data
data = filtered_data

# Save filtered data to a new file
with open("data/reference/phone_details.json", "w") as f:
    json.dump(data, f, indent=2)
