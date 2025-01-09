from datetime import datetime
import json
from typing import Dict, List, Optional
import os

class DataProcessor:
    def __init__(self, json_data: Dict):
        self.data = json_data

    def extract_item_data(self, item: Dict) -> Dict:
        """Extract relevant data from an item."""
        # Get column values
        column_values = {cv["column"]["title"]: cv for cv in item["column_values"]}

        # Extract date values
        date = self._parse_date_value(column_values.get("Date", {}).get("value"))
        start_time = self._parse_time_value(
            column_values.get("Start Time", {}).get("value")
        )
        end_time = self._parse_time_value(
            column_values.get("End Time", {}).get("value")
        )

        # Get other values
        manual_units = column_values.get("Manual units", {}).get("value") or column_values.get("Units", {}).get("value")
        auto_units = column_values.get("Auto Units", {}).get("value")
        service_type = self._get_label(column_values.get("Service Type", {}))
        provided_as = self._get_label(column_values.get("Provided As", {}))
        service_line = self._get_label(column_values.get("Service Line", {}))

        # "updates": [
        #     {
        #       "id": "3728016534",
        #       "text_body": "The Housing Coordinator (HC) contacted the client today to introduce himself and begin completing the Intake form. The client responded to the call and was greeted warmly as the HC explained his role and the purpose of the process. The HC guided the client through the questionnaire, ensuring she felt at ease and supported throughout. The client answered each question thoroughly, allowing the HC to finalize the form efficiently. Once completed, the HC informed the client that the form would be submitted to a team member who would reach out to her shortly. He expressed his gratitude for her cooperation and reassured her of his availability for further assistance if needed.",
        #       "created_at": "2024-12-27T23:36:15.000Z",
        #       "updated_at": "2024-12-27T23:36:15.000Z"
        #     },
        #     {
        #       "id": "3728016098",
        #       "text_body": "",
        #       "created_at": "2024-12-27T23:35:37.000Z",
        #       "updated_at": "2024-12-27T23:35:37.000Z"
        #     }
        #   ],

        # Get updates
        updates = item.get("updates", [])
        update_text = updates[-1].get("text_body") if updates else None

        return {
            "item_name": item.get("name"),
            "item_id": item.get("id"),
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "auto_units": auto_units,
            "manual_units": manual_units,
            "service_type": service_type,
            "provided_as": provided_as,
            "service_line": service_line,
            "update_text_body": update_text,
        }

    def _parse_date_value(self, date_str: Optional[str]) -> Optional[str]:
        """Parse date from JSON string."""
        if not date_str:
            return None
        try:
            date_data = json.loads(date_str)
            return date_data.get("date")
        except:
            return None

    def _parse_time_value(self, time_str: Optional[str]) -> Optional[str]:
        """Parse time from JSON string."""
        if not time_str:
            return None
        try:
            time_data = json.loads(time_str)
            return time_data.get("time")
        except:
            return None

    def _get_label(self, status_dict: Dict) -> Optional[str]:
        """Extract label from status dictionary."""
        return status_dict.get("label")

    def process(self) -> List[Dict]:
        """Process the entire JSON structure and return formatted data."""
        result = []

        for board in self.data["data"]["boards"]:
            for group in board["groups"]:
                group_title = group["title"]

                for item in group["items_page"]["items"]:
                    item_data = self.extract_item_data(item)
                    item_data["group_title"] = group_title
                    result.append(item_data)

        return result


# Example usage
def process_json_data(json_data: Dict) -> List[Dict]:
    processor = DataProcessor(json_data)
    return processor.process()


# Load JSON data

dir = "data/notes/raw_notes/"
for filename in os.listdir(dir):
    with open(os.path.join(dir, filename), "r") as f:
        json_data = json.load(f)

    output = process_json_data(json_data)

    output_filename = f"data/notes/cleaned_notes/{filename}"
    with open(output_filename, "w") as f:
        json.dump(output, f, indent=4)


# ----------------------------------
# to change the timezone from
import json
from datetime import datetime
import pytz
import os
from pathlib import Path


def convert_utc_to_cst(input_file):
    with open(input_file, "r") as f:
        data = json.load(f)

    utc_tz = pytz.UTC
    cst_tz = pytz.timezone("America/Chicago")

    for item in data:
        if item["date"] and item["start_time"]:
            start_dt_str = f"{item['date']} {item['start_time']}"
            start_dt = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M:%S")
            start_dt = utc_tz.localize(start_dt)
            start_cst = start_dt.astimezone(cst_tz)
            item["date"] = start_cst.strftime("%Y-%m-%d")
            item["start_time"] = start_cst.strftime("%H:%M:%S")

        if item["date"] and item["end_time"]:
            end_dt_str = f"{item['date']} {item['end_time']}"
            end_dt = datetime.strptime(end_dt_str, "%Y-%m-%d %H:%M:%S")
            end_dt = utc_tz.localize(end_dt)
            end_cst = end_dt.astimezone(cst_tz)
            item["end_time"] = end_cst.strftime("%H:%M:%S")

    output_file = input_file
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

    return output_file


def process_directory(directory_path):
    directory = Path(directory_path)
    processed_files = []

    for file_path in directory.glob("*.json"):
        if not file_path.name.endswith("_CST.json"):  # Skip already processed files
            try:
                output_file = convert_utc_to_cst(file_path)
                processed_files.append(output_file)
                print(f"Processed: {file_path.name} -> {Path(output_file).name}")
            except Exception as e:
                print(f"Error processing {file_path.name}: {str(e)}")

    return processed_files


# Usage
directory_path = "data/notes/cleaned_notes"  # Replace with your folder path
processed_files = process_directory(directory_path)
print(f"\nTotal files processed: {len(processed_files)}")


# -------------------------------------
#  to filter the notes by today date

from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
from pytz import timezone
import os
import json


def filter_json_by_date(data, target_date=None):

    # Use today's date in CST timezone if no target date provided
    if target_date is None:
        cst = timezone('US/Central')
        target_date = (datetime.now(cst).strftime("%Y-%m-%d"))
        # target_date = (datetime.now(cst) - timedelta(days=1)).strftime("%Y-%m-%d")

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
