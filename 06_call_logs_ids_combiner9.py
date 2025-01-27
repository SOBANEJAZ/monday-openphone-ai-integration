import json
import os
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
from pytz import timezone


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

import json
from dateutil.parser import parse
import pytz

# Define CST timezone
cst = pytz.timezone("America/Chicago")


# Function to determine the original datetime format
def get_datetime_format(datetime_str):
    if "T" in datetime_str and datetime_str.endswith("Z"):
        if "." in datetime_str:
            return "%Y-%m-%dT%H:%M:%S.%fZ"
        else:
            return "%Y-%m-%dT%H:%M:%S.Z"
    elif (
        datetime_str.startswith(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"))
        and "+0000" in datetime_str
    ):
        return "%a, %d %b %Y %H:%M:%S %z"
    else:
        raise ValueError(f"Unknown datetime format: {datetime_str}")


# Load the JSON data
with open("data/reference/phone_details.json", "r") as f:
    data = json.load(f)

# Iterate through each item and convert times
for item in data:
    # Parse the UTC times
    start_time_str = item["Start Time"]
    end_time_str = item["End Time"]

    # Determine the format
    start_fmt = get_datetime_format(start_time_str)
    end_fmt = get_datetime_format(end_time_str)

    # Parse the datetime strings
    start_time_utc = parse(start_time_str)
    end_time_utc = parse(end_time_str)

    # Convert to CST
    start_time_cst = start_time_utc.astimezone(cst)
    end_time_cst = end_time_utc.astimezone(cst)

    # Format back to the original format
    if start_fmt == "%Y-%m-%dT%H:%M:%S.%fZ":
        start_time_cst_str = start_time_cst.strftime("%Y-%m-%dT%H:%M:%S.%f")[
            :-3
        ] + start_time_cst.strftime("%z")
        start_time_cst_str = start_time_cst_str[:-2] + ":" + start_time_cst_str[-2:]
    elif start_fmt == "%Y-%m-%dT%H:%M:%S.Z":
        start_time_cst_str = start_time_cst.strftime("%Y-%m-%dT%H:%M:%S%z")
        start_time_cst_str = start_time_cst_str[:-2] + ":" + start_time_cst_str[-2:]
    elif start_fmt == "%a, %d %b %Y %H:%M:%S %z":
        start_time_cst_str = start_time_cst.strftime("%a, %d %b %Y %H:%M:%S %z")
    else:
        raise ValueError(f"Unknown format: {start_fmt}")

    if end_fmt == "%Y-%m-%dT%H:%M:%S.%fZ":
        end_time_cst_str = end_time_cst.strftime("%Y-%m-%dT%H:%M:%S.%f")[
            :-3
        ] + end_time_cst.strftime("%z")
        end_time_cst_str = end_time_cst_str[:-2] + ":" + end_time_cst_str[-2:]
    elif end_fmt == "%Y-%m-%dT%H:%M:%S.Z":
        end_time_cst_str = end_time_cst.strftime("%Y-%m-%dT%H:%M:%S%z")
        end_time_cst_str = end_time_cst_str[:-2] + ":" + end_time_cst_str[-2:]
    elif end_fmt == "%a, %d %b %Y %H:%M:%S %z":
        end_time_cst_str = end_time_cst.strftime("%a, %d %b %Y %H:%M:%S %z")
    else:
        raise ValueError(f"Unknown format: {end_fmt}")

    # Update the item with CST times
    item["Start Time"] = start_time_cst_str
    item["End Time"] = end_time_cst_str

# Write the updated data back to the JSON file
with open("data/reference/phone_details.json", "w") as f:
    json.dump(data, f, indent=4)

# ---------------------
# filter_json_by_date

# def filter_json_by_date(data: List[Dict[Any, Any]], target_date: str = None) -> List[Dict[Any, Any]]:


def filter_json_by_date(data, target_date=None):

    # Use today's date in CST timezone if no target date provided
    if target_date is None:
        cst = timezone("US/Central")
        # ------------------------
        # ------------------------
        # ------------------------
        # ------------------------
        # ------------------------
        # ------------------------
        # ------------------------
        # ------------------------
        # target_date = (datetime.now(cst).strftime("%Y-%m-%d"))
        target_date = (datetime.now(cst) - timedelta(days=14)).strftime("%Y-%m-%d")

    # Validate target date format
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("target_date must be in YYYY-MM-DD format")
    filtered_data = []
    for item in data:
        start_time_str = item.get("Start Time")
        if start_time_str:
            try:
                # Parse the Start Time string
                start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S.%f%z")
                # Extract the date part
                item_date = start_time.strftime("%Y-%m-%d")
                if item_date == target_date:
                    filtered_data.append(item)
            except ValueError:
                # Skip items with invalid date formats
                continue
        else:
            # Skip items without "Start Time" key
            continue

    return filtered_data


# Read the JSON data from file
with open("data/reference/phone_details.json", "r") as f:
    data = json.load(f)

# Filter the data
filtered_data = filter_json_by_date(data)

# Write the filtered data to a new JSON file
with open("data/reference/phone_details.json", "w") as f:
    json.dump(filtered_data, f, indent=4)
