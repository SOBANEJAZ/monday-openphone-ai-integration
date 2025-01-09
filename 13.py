import os
import json
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment variables
load_dotenv()
api = os.getenv("MONDAY_API_KEY")
url = "https://api.monday.com/v2"
headers = {
    "Content-Type": "application/json",
    "Authorization": api,
}

# Status mapping dictionaries
SERVICE_TYPE_MAP = {"Transitioning": "0", "Sustaining": "1", "Consultation": "2"}

PROVIDED_AS_MAP = {
    "Direct/Remote": "0",
    "Direct Remote": "0",
    "indirect": "1",
    "Direct/In-Person": "2",
}

SEVERITY_MAP = {"high": "0", "medium": "1", "low": "2", "good note": "3"}

# New severity mapping for AI analysis
AI_start_SEVERITY_MAP = {"Flagged": "2", "Good": "3"}
AI_end_SEVERITY_MAP = {"Flagged": "0", "Good": "3"}


def update_column_value(item_id, board_id, column_id, value):
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
        value,
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


def format_datetime(date_str, time_str):
    if not date_str or not time_str:
        return None
    try:
        datetime_str = f"{date_str} {time_str}"
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error formatting datetime {datetime_str}: {str(e)}")
        return None


def get_mapped_status(value, status_map, default="3"):
    if not value:
        return default
    return status_map.get(value, default)


def update_all_columns(item_id, board_id, note, board_id_from_filename):
    # Format date for date column
    date_value, year_value = format_date_values(note.get("date", ""))
    if date_value:
        update_column_value(item_id, board_id, "date", date_value)
    if year_value:
        update_column_value(item_id, board_id, "year", year_value)

    # Update start time
    start_time = format_datetime(note.get("date"), note.get("start_time"))
    if start_time:
        update_column_value(item_id, board_id, "date_13", start_time)

    # Update end time
    end_time = format_datetime(note.get("date"), note.get("end_time"))
    if end_time:
        update_column_value(item_id, board_id, "date_19", end_time)

    # Update manual units
    manual_units = note.get("manual_units", "").strip('"')
    if manual_units:
        update_column_value(item_id, board_id, "numbers1", manual_units)

    # Update service type status
    service_type_value = get_mapped_status(note.get("service_type"), SERVICE_TYPE_MAP)
    update_column_value(item_id, board_id, "status80", service_type_value)

    # Update provided as status
    provided_as_value = get_mapped_status(note.get("provided_as"), PROVIDED_AS_MAP)
    update_column_value(item_id, board_id, "status4", provided_as_value)

    # Update severity status for transcripts
    severity_value = get_mapped_status(note.get("transcript_severity"), SEVERITY_MAP)
    update_column_value(item_id, board_id, "severity_flags_mkks6sc7", severity_value)

    # Update issue_description_mkm0j7qm column with transcript reason
    transcript_reason = note.get("transcript_reason", "")
    if transcript_reason:
        update_column_value(
            item_id, board_id, "issue_description_mkm0j7qm", transcript_reason
        )

    # Update original text body
    original_text_body = note.get("update_text_body", "")
    if original_text_body:
        update_column_value(
            item_id, board_id, "original_note_mkm0z2v3", original_text_body
        )

    # Update link
    link = note.get("item_id", "")
    item_link = f"https://simplehealthservices.monday.com/boards/{board_id_from_filename}/pulses/{link}"
    update_column_value(item_id, board_id, "link_to_original_note_mkm09qb0", item_link)

    # Update start and end reason text columns
    start_reason = note.get("start_reason", "")
    if start_reason:
        update_column_value(item_id, board_id, "text_mkm1vk1y", start_reason)

    end_reason = note.get("end_reason", "")
    if end_reason:
        update_column_value(item_id, board_id, "text_mkm1d8wd", end_reason)

    # Update start severity flag
    start_severity = note.get("start_severity", "Good")
    start_severity_value = AI_start_SEVERITY_MAP.get(start_severity, "3")
    update_column_value(
        item_id, board_id, "dup__of_severity_flags_mkm19yh", start_severity_value
    )

    # Update end severity flag
    end_severity = note.get("end_severity", "Good")
    end_severity_value = AI_end_SEVERITY_MAP.get(end_severity, "3")
    update_column_value(item_id, board_id, "status_mkm1fy0n", end_severity_value)


def format_date_values(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        date_value = date_obj.strftime("%-d %b")
        year_value = date_obj.strftime("%Y")
        return date_value, year_value
    except Exception as e:
        print(f"Error formatting date {date_str}: {str(e)}")
        return None, None


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

        for note in notes:
            group_title = note.get("group_title", "")

            if not group_title:
                print(f"Skipping note without title in {filename}")
                continue

            mutation = """
            mutation {
                create_item(
                    board_id: 8139951792,
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
                        item_id, "8139951792", note, board_id_from_filename
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
    dir_path = "Output/"  # Update this to your directory path
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
