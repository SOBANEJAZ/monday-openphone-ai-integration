import json
import os
from collections import defaultdict


def process_json_files(main_json_path, notes_dir):
    # Read main JSON file
    with open(main_json_path, "r") as f:
        main_data = json.load(f)

    # Group items by Board_id
    board_id_groups = defaultdict(list)
    for item in main_data:
        if "Board_id" in item:
            board_id_groups[item["Board_id"]].append(item)

    # Process each file in notes directory
    for filename in os.listdir(notes_dir):
        if filename.endswith(".json"):
            board_id = filename[:-5]  # Remove .json extension
            file_path = os.path.join(notes_dir, filename)
            try:
                # Read existing notes file
                with open(file_path, "r") as f:
                    existing_data = json.load(f)

                # Extract the actual notes array, regardless of nesting
                notes_array = None
                if isinstance(existing_data, dict):
                    # Navigate through nested "notes" keys to find the array
                    current = existing_data
                    while isinstance(current, dict) and "notes" in current:
                        current = current["notes"]
                    if isinstance(current, list):
                        notes_array = current
                    elif "notes" in current and isinstance(current["notes"], list):
                        notes_array = current["notes"]

                # If we couldn't find a notes array, use the entire existing data
                if notes_array is None:
                    notes_array = (
                        existing_data if isinstance(existing_data, list) else []
                    )

                # Create output structure
                output_data = {
                    "notes": notes_array,
                    "call_transcripts": board_id_groups.get(board_id, []),
                }

                # Write updated data back to file
                with open(file_path, "w") as f:
                    json.dump(output_data, f, indent=2)
                print(f"Processed {filename}")
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")


# Usage
main_json_path = "data/reference/phone_details.json"  # Path to your main JSON file
notes_dir = "data/notes/filtered_notes"  # Path to directory containing note files
process_json_files(main_json_path, notes_dir)
