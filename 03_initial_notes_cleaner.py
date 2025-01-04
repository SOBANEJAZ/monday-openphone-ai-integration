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
        manual_units = column_values.get("Manual units", {}).get("value")
        auto_units = column_values.get("Auto Units", {}).get("value")
        service_type = self._get_label(column_values.get("Service Type", {}))
        provided_as = self._get_label(column_values.get("Provided As", {}))
        service_line = self._get_label(column_values.get("Service Line", {}))

        # Get updates
        updates = item.get("updates", [])
        update_text = updates[0].get("text_body") if updates else None

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

dir = "initial_data/raw_notes/"
for filename in os.listdir(dir):
    with open(os.path.join(dir, filename), "r") as f:
        json_data = json.load(f)
    
    output = process_json_data(json_data)
    
    output_filename = f"initial_data/cleaned_notes/{filename}"
    with open(output_filename, "w") as f:
        json.dump(output, f, indent=4)