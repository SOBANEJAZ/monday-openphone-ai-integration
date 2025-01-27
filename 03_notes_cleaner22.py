from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import os
from typing import Any
from pytz import timezone
import pytz
from pathlib import Path




class DataProcessor:

    def __init__(self, json_data: Dict):
        self.data = json_data

    def extract_item_data(self, item: Dict) -> Dict:
        """Extract relevant data from an item."""
        # Get column values
        column_values = {
            cv["column"]["title"]: cv
            for cv in item["column_values"]
        }

        # Extract date values
        date = self._parse_date_value(
            column_values.get("Date", {}).get("value"))
        start_time = self._parse_time_value(
            column_values.get("Start Time", {}).get("value"))
        end_time = self._parse_time_value(
            column_values.get("End Time", {}).get("value"))
        

        # Get other values
        manual_units = column_values.get(
            "Manual units", {}).get("value") or column_values.get(
                "Units", {}).get("value") or column_values.get(
                    "Manual Units", {}).get("value")
        service_type = self._get_label(column_values.get("Service Type", {}))
        provided_as = self._get_label(column_values.get("Provided As", {}))
        service_line = self._get_label(column_values.get("Service Line", {}))
        session_status = self._get_label(column_values.get("Session Status", {}))
        Signature = self._get_label(column_values.get("Signature", {}))
        

        # Get updates
        updates = item.get("updates", [])
        update_text = updates[-1].get("text_body") if updates else None
        update_creation_time = updates[-1].get(
            "created_at") if updates else None

        return {
            "item_name": item.get("name"),
            "item_id": item.get("id"),
            "session_creation_time": item.get("created_at"),
            "update_creation_time": update_creation_time,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "manual_units": manual_units,
            "service_type": service_type,
            "provided_as": provided_as,
            "service_line": service_line,
            "session_status": session_status,
            "signature": Signature,
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


def process_json_data(json_data: Dict) -> List[Dict]:
    """Process the JSON data using DataProcessor."""
    processor = DataProcessor(json_data)
    return processor.process()


def convert_utc_to_cst(input_file):
    """Convert timestamps from UTC to CST."""
    with open(input_file, "r") as f:
        data = json.load(f)

    utc_tz = pytz.UTC
    cst_tz = pytz.timezone("America/Chicago")

    for item in data:
        # Handle session creation time
        if item["session_creation_time"]:
            try:
                # Parse the UTC timestamp
                session_dt = datetime.strptime(
                    item["session_creation_time"],
                    "%Y-%m-%dT%H:%M:%SZ",  # Format for UTC ISO timestamps
                )
                session_dt = utc_tz.localize(session_dt)
                session_cst = session_dt.astimezone(cst_tz)
                item["session_creation_time"] = session_cst.strftime(
                    "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(
                    f"Error converting session_creation_time: {item['session_creation_time']}"
                )

        # Handle update creation time
        if item["update_creation_time"]:
            try:
                # Parse the UTC timestamp with milliseconds
                update_dt = datetime.strptime(
                    item["update_creation_time"].split(".")[0],
                    "%Y-%m-%dT%H:%M:%S")
                update_dt = utc_tz.localize(update_dt)
                update_cst = update_dt.astimezone(cst_tz)
                item["update_creation_time"] = update_cst.strftime(
                    "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(
                    f"Error converting update_creation_time: {item['update_creation_time']}"
                )

        # Handle date and times
        if item["date"] and item["start_time"]:
            try:
                # Combine date and time
                start_dt_str = f"{item['date']} {item['start_time']}"
                start_dt = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M:%S")
                start_dt = utc_tz.localize(start_dt)
                start_cst = start_dt.astimezone(cst_tz)

                # Update both date and time
                item["date"] = start_cst.strftime("%Y-%m-%d")
                item["start_time"] = start_cst.strftime("%H:%M:%S")
            except ValueError:
                print(f"Error converting start time: {start_dt_str}")

        if item["date"] and item["end_time"]:
            try:
                end_dt_str = f"{item['date']} {item['end_time']}"
                end_dt = datetime.strptime(end_dt_str, "%Y-%m-%d %H:%M:%S")
                end_dt = utc_tz.localize(end_dt)
                end_cst = end_dt.astimezone(cst_tz)
                item["end_time"] = end_cst.strftime("%H:%M:%S")
            except ValueError:
                print(f"Error converting end time: {end_dt_str}")

    output_file = input_file
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

    return output_file


def process_directory(directory_path):
    """Process all JSON files in a directory."""
    directory = Path(directory_path)
    processed_files = []

    for file_path in directory.glob("*.json"):
        try:
            output_file = convert_utc_to_cst(file_path)
            processed_files.append(output_file)
            print(f"Processed: {file_path.name} -> {Path(output_file).name}")
        except Exception as e:
            print(f"Error processing {file_path.name}: {str(e)}")

    return processed_files


def filter_json_by_date(data, target_date=None):
    if target_date is None:
        cst = timezone("US/Central")
        # ------------------------
        # ------------------------
        # ------------------------
        # ------------------------
        # ------------------------
        # ------------------------
        # ------------------------
    # target_date = (datetime.now(cst).strftime("%Y-%m-%d"))
    target_date = (datetime.now(cst) - timedelta(days=1)).strftime("%Y-%m-%d")

# Validate target date format
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("target_date must be in YYYY-MM-DD format")    
    filtered_data = [item for item in data if item.get("date") == target_date]
    return filtered_data


# Main execution
if __name__ == "__main__":
    # Step 1: Process raw JSON files
    raw_dir = "data/notes/raw_notes/"
    for filename in os.listdir(raw_dir):
        with open(os.path.join(raw_dir, filename), "r") as f:
            json_data = json.load(f)

        output = process_json_data(json_data)
        output_filename = f"data/notes/cleaned_notes/{filename}"
        with open(output_filename, "w") as f:
            json.dump(output, f, indent=4)

    # Step 2: Convert timezones
    cleaned_dir = "data/notes/cleaned_notes"
    processed_files = process_directory(cleaned_dir)
    print(
        f"\nTotal files processed for timezone conversion: {len(processed_files)}"
    )

    # Step 3: Filter by date
    filtered_dir = "data/notes/filtered_notes/"
    for filename in os.listdir(cleaned_dir):
        with open(os.path.join(cleaned_dir, filename), "r") as f:
            data = json.load(f)

        filtered_data = filter_json_by_date(data)

        with open(os.path.join(filtered_dir, filename), "w") as f:
            json.dump(filtered_data, f, indent=4)