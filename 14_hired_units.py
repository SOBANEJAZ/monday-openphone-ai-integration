import os
import json

# Specify the directory containing the JSON files
directory = 'Output_units'

# List all JSON files in the directory
json_files = [f for f in os.listdir(directory) if f.endswith('.json')]

for filename in json_files:
    # Build the full file path
    file_path = os.path.join(directory, filename)

    # Open and load the JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Access the "notes" list
    notes = data.get("notes", [])

    # Calculate the total sum of "manual_units"
    total_sum = 0.0
    for item in notes:
        manual_units = item.get("manual_units", None)
        if manual_units is None:
            continue  # Treat as 0
        elif isinstance(manual_units, str):
            # Remove quotes and convert to float
            manual_units = manual_units.strip('"')
            try:
                manual_units = float(manual_units)
                total_sum += manual_units
            except ValueError:
                # Invalid manual_units, skip
                pass
        elif isinstance(manual_units, (int, float)):
            total_sum += manual_units
        else:
            # Unsupported data type, skip
            pass

    # Append "total_units" to each item in "notes"
    for item in notes:
        item["total_units"] = total_sum

    # Write the modified data back to the JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    import os
    import json

    input_directory = 'Output_units/'
    output_directory = 'Output_units'

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    json_files = [f for f in os.listdir(input_directory) if f.endswith('.json')]

    hired_units = 32.0

    for filename in json_files:
        input_path = os.path.join(input_directory, filename)
        output_path = os.path.join(output_directory, filename)

        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if "notes" in data and isinstance(data["notes"], list) and len(data["notes"]) > 0:
                first_note = data["notes"][0]
                total_units = first_note.get("total_units", None)
                if total_units is None:
                    first_note["units_status"] = "Flagged"
                    first_note["units_reason"] = "The 'total_units' key is missing in the note."
                else:
                    total_units = float(total_units)
                    if total_units < hired_units:
                        first_note["units_status"] = "Flagged"
                        difference = hired_units - total_units
                        first_note["units_reason"] = f"There are {difference:.1f} less units in total units than the hired units."
                    elif total_units > hired_units:
                        first_note["units_status"] = "Flagged"
                        difference = total_units - hired_units
                        first_note["units_reason"] = f"There are {difference:.1f} more units in total units than the hired units."
                    else:
                        first_note["units_status"] = "Good"
                        first_note["units_reason"] = "The hired units match the daily total units."

                # Create a new "notes" list with only the first note
                data["notes"] = [first_note]
            else:
                # Handle cases where "notes" is not present, not a list, or empty
                # Set "notes" to an empty list
                data["notes"] = []

            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)

            print(f"Processed file: {filename}")

        except Exception as e:
            print(f"Error processing file {filename}: {e}")