
# -------------------------------------
#  to filter the notes by today date

from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
from pytz import timezone
import os
import json


def filter_json_by_date(
    data: List[Dict[Any, Any]], target_date: str = None
) -> List[Dict[Any, Any]]:

    # Use today's date in CST timezone if no target date provided
    if target_date is None:
        cst = timezone('US/Central')
        target_date = (datetime.now(cst) - timedelta(days=1)).strftime("%Y-%m-%d")

    # Validate target date format
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("target_date must be in YYYY-MM-DD format")

    # Filter items
    filtered_data = [item for item in data if item.get("date") == target_date]

    return filtered_data

# Example usage
dir = "data/notes/cleaned_notes/"
for filename in os.listdir(dir):
    with open(os.path.join(dir, filename), "r") as f:
        data = json.load(f)

    filtered_data = filter_json_by_date(data)

    with open(f"data/notes/filtered_notes/{filename}", "w") as f:
        json.dump(filtered_data, f, indent=4)
