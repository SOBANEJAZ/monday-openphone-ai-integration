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

# Existing status mapping dictionaries
SERVICE_TYPE_MAP = {
    "Transitioning": "0",
    "Sustaining": "1",
    "Consultation": "2"
}

PROVIDED_AS_MAP = {
    "Direct/Remote": "0",
    "Direct Remote": "0",
    "indirect": "1",
    "Direct/In-Person": "3",
}
FLAG_STATUS_MAP = {"Good": "1", "Flagged": "0"}
FLAG_STATUS_MAP_TRANSCRIPTS = {"Good": "2", "Flagged": "0"}
SEVERITY_MAP = {"high": "0", "medium": "1", "low": "2", "good note": "3"}

# New severity mapping for AI analysis
AI_start_SEVERITY_MAP = {"Flagged": "2", "Good": "3"}
AI_end_SEVERITY_MAP = {"Flagged": "0", "Good": "3"}

# New billing status mapping
BILLING_STATUS_MAP = {"overbilled": "2", "good": "1"}

# New status mapping for housing services
HOUSING_SERVICES_MAP = {
    "Developing a housing transition plan":
    "1",
    "Developing a housing transition plan*":
    "1",
    "Supporting the person in applying for benefits to afford their housing, including helping the person determine which benefits they may be eligible for":
    "110",
    "Supporting the person in applying for benefits to afford their housing, including helping the person determine which benefits they may be eligible for*":
    "110",
    "Assisting the person with the housing search and application process":
    "156",
    "Assisting the person with the housing search and application process*":
    "156",
    "":
    "5",
    "Assisting the person with tenant screening and housing assessments":
    "0",
    "Assisting the person with tenant screening and housing assessments*":
    "0",
    "Providing transportation with the person receiving services present and discussing housing related issues":
    "7",
    "Providing transportation with the person receiving services present and discussing housing related issues*":
    "7",
    "Helping the person understand and develop a budget":
    "2",
    "Helping the person understand and develop a budget*":
    "2",
    "Helping the person understand and negotiate a lease":
    "4",
    "Helping the person understand and negotiate a lease*":
    "4",
    "Helping the person meet and build a relationship with a prospective landlord":
    "6",
    "Helping the person meet and build a relationship with a prospective landlord*":
    "6",
    "Promoting/supporting cultural practice needs and understandings with prospective landlords, property managers":
    "3",
    "Promoting/supporting cultural practice needs and understandings with prospective landlords, property managers*":
    "3",
    "Helping the person find funding for deposits":
    "8",
    "Helping the person find funding for deposits*":
    "8",
    "Helping the person organize their move":
    "9",
    "Helping the person organize their move*":
    "9",
    "Researching possible housing options for the person":
    "10",
    "Researching possible housing options for the person*":
    "10",
    "Contacting possible housing options for the person":
    "11",
    "Contacting possible housing options for the person*":
    "11",
    "Identifying resources to pay for deposits or home goods":
    "12",
    "Identifying resources to pay for deposits or home goods*":
    "12",
    "Identifying resources to cover moving expenses":
    "13",
    "Identifying resources to cover moving expenses*":
    "13",
    "Completing housing applications on behalf of the service recipient":
    "14",
    "Completing housing applications on behalf of the service recipient*":
    "14",
    "Working to expunge records or access reasonable accommodations":
    "15",
    "Working to expunge records or access reasonable accommodations*":
    "15",
    "Identifying services and benefits that will support the person with housing instability":
    "16",
    "Identifying services and benefits that will support the person with housing instability*":
    "16",
    "Ensuring the new living arrangement is safe for the person and ready for move-in":
    "17",
    "Ensuring the new living arrangement is safe for the person and ready for move-in*":
    "17",
    "Arranging for adaptive house related accommodations required by the person":
    "18",
    "Arranging for adaptive house related accommodations required by the person*":
    "18",
    "Arranging for assistive technology required by the person":
    "19",
    "Arranging for assistive technology required by the person*":
    "19",
    "Staff Meeting":
    "101",
    "Staff Meeting*":
    "101",
    "Intake Meeting":
    "102",
    "Intake Meeting*":
    "102",
    "Other":
    "158",
    "Other*":
    "158",
    "Developing, updating and modifying the housing support and crisis/safety plan on a regular basis":
    "104",
    "Developing, updating and modifying the housing support and crisis/safety plan on a regular basis*":
    "104",
    "Preventing and early identification of behaviors that may jeopardize continued housing":
    "106",
    "Preventing and early identification of behaviors that may jeopardize continued housing*":
    "106",
    "Educating and training on roles, rights, and responsibilities of the tenant and property manager":
    "107",
    "Educating and training on roles, rights, and responsibilities of the tenant and property manager*":
    "107",
    "Transportation with the person receiving services present and discussing housing related issues":
    "108",
    "Transportation with the person receiving services present and discussing housing related issues*":
    "108",
    "Promoting/supporting cultural practice needs and understandings with landlords, property managers and neighbors":
    "109",
    "Promoting/supporting cultural practice needs and understandings with landlords, property managers and neighbors*":
    "109",
    "Coaching to develop and maintain key relationships with property managers and neighbors":
    "154",
    "Coaching to develop and maintain key relationships with property managers and neighbors*":
    "154",
    "Advocating with community resources to prevent eviction when housing is at risk and maintain person's safety":
    "151",
    "Advocating with community resources to prevent eviction when housing is at risk and maintain person's safety*":
    "151",
    "Assistance with the housing recertification processes":
    "152",
    "Assistance with the housing recertification processes*":
    "152",
    "Continued training on being a good tenant, lease compliance, and household management":
    "159",
    "Continued training on being a good tenant, lease compliance, and household management*":
    "159",
    "Supporting the person to apply for benefits to retain housing":
    "155",
    "Supporting the person to apply for benefits to retain housing*":
    "155",
    "Supporting the person to understand and maintain/ increase income and benefits to retain housing":
    "157",
    "Supporting the person to understand and maintain/ increase income and benefits to retain housing*":
    "157",
    "Supporting the building of natural housing supports and resources in the community including building supports and resources related to a person's culture and identity":
    "153",
    "Supporting the building of natural housing supports and resources in the community including building supports and resources related to a person's culture and identity*":
    "153",
    "Working with property manager or landlord to promote housing retention":
    "105",
    "Working with property manager or landlord to promote housing retention*":
    "105",
    "Arranging for assistive technology":
    "160",
    "Arranging for assistive technology*":
    "160",
    "Arranging for adaptive house related accommodations.":
    "103",
    "Arranging for adaptive house related accommodations.*":
    "103"
}

# New status mapping for flag statuses


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
        response = requests.post(url,
                                 json={"query": mutation},
                                 headers=headers)
        response_data = response.json()

        if response.status_code == 200 and "data" in response_data:
            print(
                f"Updated {column_id} column for item {item_id} with value {value}"
            )
            return True
        else:
            error_message = response_data.get("errors",
                                              [{
                                                  "message": "Unknown error"
                                              }])[0]["message"]
            print(
                f"Error updating {column_id} for item {item_id}: {error_message}"
            )
            return False

    except Exception as e:
        print(f"Error updating {column_id} for item {item_id}: {str(e)}")
        return False


def format_datetime(date_str, time_str):
    if date_str is None or time_str is None:
        return None
    try:
        datetime_str = f"{date_str} {time_str}"
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error formatting datetime: {str(e)}")
        return None


def get_mapped_status(value, status_map, default="3"):
    if value is None:
        return default
    return status_map.get(value, default)


def safe_get(note, key, default=None):
    """Safely get a value from the note dictionary"""
    value = note.get(key, default)
    return value if value is not None else default


def update_all_columns(item_id, board_id, note, board_id_from_filename):
    try:
        # [Previous column updates remain the same...]

        # Format date for date column
        date_str = safe_get(note, "date")
        if date_str is not None:
            date_value, year_value = format_date_values(date_str)
            if date_value is not None:
                update_column_value(item_id, board_id, "date", date_value)
            if year_value is not None:
                update_column_value(item_id, board_id, "year", year_value)

        # Update start time
        start_time = format_datetime(safe_get(note, "date"),
                                     safe_get(note, "start_time"))
        if start_time is not None:
            update_column_value(item_id, board_id, "date_13", start_time)

        # Update end time
        end_time = format_datetime(safe_get(note, "date"),
                                   safe_get(note, "end_time"))
        if end_time is not None:
            update_column_value(item_id, board_id, "date_19", end_time)

        # Update manual units
        manual_units = safe_get(note, "manual_units")
        if manual_units is not None:
            manual_units_str = str(manual_units).strip('"')
            update_column_value(item_id, board_id, "numbers1",
                                manual_units_str)

        # Update service type status
        service_type_value = get_mapped_status(safe_get(note, "service_type"),
                                               SERVICE_TYPE_MAP)
        if service_type_value is not None:
            update_column_value(item_id, board_id, "status80",
                                service_type_value)

        # Update provided as status
        provided_as_value = get_mapped_status(safe_get(note, "provided_as"),
                                              PROVIDED_AS_MAP)
        if provided_as_value is not None:
            update_column_value(item_id, board_id, "status4",
                                provided_as_value)

        # Update severity status for transcripts
        severity_value = get_mapped_status(
            safe_get(note, "transcript_severity"), FLAG_STATUS_MAP_TRANSCRIPTS)
        if severity_value is not None:
            update_column_value(item_id, board_id, "severity_flags_mkks6sc7",
                                severity_value)

        # Update issue_description with transcript reason
        transcript_reason = safe_get(note, "transcript_reason")
        if transcript_reason is not None:
            update_column_value(item_id, board_id,
                                "issue_description_mkm0j7qm",
                                transcript_reason)

        # Update original text body
        original_text_body = safe_get(note, "update_text_body")
        if original_text_body is not None:
            update_column_value(item_id, board_id, "original_note_mkm0z2v3",
                                original_text_body)

        # Update link
        link = safe_get(note, "item_id")
        if link is not None:
            item_link = f"https://simplehealthservices.monday.com/boards/{board_id_from_filename}/pulses/{link}"
            update_column_value(item_id, board_id,
                                "link_to_original_note_mkm09qb0", item_link)

        # Update start and end reason text columns
        start_reason = safe_get(note, "start_reason")
        if start_reason is not None:
            update_column_value(item_id, board_id, "text_mkm1vk1y",
                                start_reason)

        end_reason = safe_get(note, "end_reason")
        if end_reason is not None:
            update_column_value(item_id, board_id, "text_mkm1d8wd", end_reason)

        # Update start severity flag
        start_severity = safe_get(note, "start_severity", "Good")
        if start_severity is not None:
            start_severity_value = AI_start_SEVERITY_MAP.get(
                start_severity, "3")
            update_column_value(item_id, board_id,
                                "dup__of_severity_flags_mkm19yh",
                                start_severity_value)

        # Update end severity flag
        end_severity = safe_get(note, "end_severity", "Good")
        if end_severity is not None:
            end_severity_value = AI_end_SEVERITY_MAP.get(end_severity, "3")
            update_column_value(item_id, board_id, "status_mkm1fy0n",
                                end_severity_value)

        # Update billing reason
        billing_reason = safe_get(note, "billing_reason")
        if billing_reason is not None:
            update_column_value(item_id, board_id, "text_mkm2sxx6",
                                billing_reason)

        # Update billing improved
        billing_improved = safe_get(note, "billing_improved")
        if billing_improved is not None:
            update_column_value(item_id, board_id, "text_mkm2ez8j",
                                billing_improved)

        # Update billing status
        billing_status = safe_get(note, "billing_severity")
        if billing_status is not None:
            billing_status_value = BILLING_STATUS_MAP.get(
                billing_status.lower(), "")
            update_column_value(item_id, board_id, "status_mkm2zs2v",
                                billing_status_value)

        # New column updates start here

        # Update service reason text
        service_reason = safe_get(note, "service_reason")
        if service_reason is not None:
            update_column_value(item_id, board_id, "long_text_mkm545rp",
                                service_reason)

        # Update columns reason text
        columns_reason = safe_get(note, "columns_reason")
        if columns_reason is not None:
            update_column_value(item_id, board_id, "text_mkm5tqa7",
                                columns_reason)

        # Update housing services status
        housing_service = safe_get(note, "service_line")
        if housing_service is not None:
            housing_service_value = HOUSING_SERVICES_MAP.get(
                housing_service, "5")  # Default to "5" if not found
            update_column_value(item_id, board_id, "status_mkm5hyx0",
                                housing_service_value)

        # Update flag status columns
        flag_status1 = safe_get(note, "service_severity")
        if flag_status1 is not None:
            flag_status_value1 = FLAG_STATUS_MAP.get(
                flag_status1, "1")  # Default to "Good" if not found
            update_column_value(item_id, board_id, "status_mkm64aec",
                                flag_status_value1)

        flag_status2 = safe_get(note, "columns_severity")
        if flag_status2 is not None:
            flag_status_value2 = FLAG_STATUS_MAP.get(
                flag_status2, "1")  # Default to "Good" if not found
            update_column_value(item_id, board_id, "status_mkm5aj0m",
                                flag_status_value2)

    except Exception as e:
        print(f"Error in update_all_columns for item {item_id}: {str(e)}")
        return False

    return True


def format_date_values(date_str):
    if date_str is None:
        return None, None
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

        board_id_from_filename = os.path.splitext(
            os.path.basename(filename))[0]

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
                response = requests.post(url,
                                         json={"query": mutation},
                                         headers=headers)
                response_data = response.json()

                if response.status_code == 200 and "data" in response_data:
                    item_id = response_data["data"]["create_item"]["id"]
                    created_items.append(item_id)
                    print(
                        f"Created item with ID: {item_id} for group {group_id}, title: {group_title}"
                    )

                    update_all_columns(item_id, "8139951792", note,
                                       board_id_from_filename)

                else:
                    error_message = response_data.get(
                        "errors", [{
                            "message": "Unknown error"
                        }])[0]["message"]
                    print(
                        f"Error creating item for {filename}, note {note.get('item_name')}: {error_message}"
                    )

            except requests.exceptions.RequestException as e:
                print(f"Request error for {filename}: {str(e)}")
            except Exception as e:
                print(
                    f"Unexpected error processing note in {filename}: {str(e)}"
                )

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
