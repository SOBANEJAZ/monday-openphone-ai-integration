import os
import json
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
from pytz import timezone

cst = timezone("US/Central")
# target_date = (datetime.now(cst).strftime("%Y-%m-%d"))
date_str = (datetime.now(cst) - timedelta(days=8)).strftime("%Y-%m-%d")

# Load environment variables
load_dotenv()
api = os.getenv("MONDAY_API_KEY")
url = "https://api.monday.com/v2"
headers = {
    "Content-Type": "application/json",
    "Authorization": api,
}

# New status mapping for flag statuses
FLAG_STATUS_MAP = {"Good": "1", "Flagged": "0"}


def update_column_value(item_id, board_id, column_id, value):
    if value is None:
        print(f"Skipping update for {column_id} due to null value")
        return True

    mutation = """
    mutation {
        change_simple_column_value (
            item_id: %s, 
            board_id: %s, 
            column_id: "%s", 
            value: "%s"
        ) {
            id
        }
    }
    """ % (
        item_id,
        board_id,
        column_id,
        str(value),
    )

    try:
        response = requests.post(url, json={"query": mutation}, headers=headers)
        response_data = response.json()

        if response.status_code == 200 and "data" in response_data:
            print(f"Updated {column_id} column for item {item_id} with value {value}")
            return True
        else:
            error_message = response_data.get("errors", [{"message": "Unknown error"}])[
                0
            ]["message"]
            print(f"Error updating {column_id} for item {item_id}: {error_message}")
            return False

    except Exception as e:
        print(f"Error updating {column_id} for item {item_id}: {str(e)}")
        return False


def safe_get(note, key, default=None):
    """Safely get a value from the note dictionary"""
    value = note.get(key, default)
    return value if value is not None else default


def update_all_columns(item_id, board_id, note, board_id_from_filename):
    try:
        if date_str is not None:
            update_column_value(item_id, board_id, "date4", date_str)

        units_added = safe_get(note, "total_units")
        if units_added is not None:
            update_column_value(item_id, board_id, "numbers_mkm6axzx", units_added)

        units_status = safe_get(note, "units_status")
        if units_status is not None:
            units_status_value = FLAG_STATUS_MAP.get(
                units_status, "1"
            )  # Default to "Good" if not found
            update_column_value(item_id, board_id, "status_mkm61j", units_status_value)

        units_reason = safe_get(note, "units_reason")
        if units_reason is not None:
            update_column_value(item_id, board_id, "long_text_mkm6wg9t", units_reason)

    except Exception as e:
        print(f"Error in update_all_columns for item {item_id}: {str(e)}")
        return False

    return True


def process_json_file(filename):
    file_path = filename
    created_items = []
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        notes = data.get("notes", [])
        if not notes:
            print(f"No notes found in {filename}")
            return created_items
        group_id = notes[0].get("group_name", "")
        if not group_id:
            print(f"No group_id found in {filename}")
            return created_items

        board_id_from_filename = os.path.splitext(os.path.basename(filename))[0]
        print(f"Processing {board_id_from_filename} with group_id: {group_id}")

        for day_number, note in enumerate(notes, 1):
            group_title = "Daily Units Report"
            mutation = """
            mutation {
                create_item(
                    board_id: 8198737855,
                    group_id: "%s",
                    item_name: "%s") {
                    id
                }
            }
            """ % (
                group_id,
                group_title.replace('"', '\\"'),
            )
            try:
                response = requests.post(url, json={"query": mutation}, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and "data" in response_data:
                    item_id = response_data["data"]["create_item"]["id"]
                    created_items.append(item_id)
                    print(
                        f"Created item with ID: {item_id} for group {group_id}, title: {group_title}"
                    )
                    update_all_columns(
                        item_id, "8198737855", note, board_id_from_filename
                    )
                else:
                    error_message = response_data.get(
                        "errors", [{"message": "Unknown error"}]
                    )[0]["message"]
                    print(
                        f"Error creating item for {filename}, note {note.get('item_name')}: {error_message}"
                    )
            except requests.exceptions.RequestException as e:
                print(f"Request error for {filename}: {str(e)}")
            except Exception as e:
                print(f"Unexpected error processing note in {filename}: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in {filename}: {str(e)}")
    except Exception as e:
        print(f"Error processing file {filename}: {str(e)}")
    return created_items


def main():
    dir_path = "Output_units/"  # Update this to your directory path
    all_created_items = []

    for filename in os.listdir(dir_path):
        if filename.endswith(".json"):
            full_path = os.path.join(dir_path, filename)
            print(f"\nProcessing {filename}...")
            created_items = process_json_file(full_path)
            all_created_items.extend(created_items)

    print("\nAll created item IDs in order:")
    for item_id in all_created_items:
        print(item_id)
    print(f"\nTotal items created: {len(all_created_items)}")


if __name__ == "__main__":
    main()
