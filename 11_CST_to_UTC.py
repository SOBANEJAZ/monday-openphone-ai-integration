import json
from datetime import datetime
import pytz
import os


# Function to convert time from one timezone to another
def convert_time(date_str, time_str, timezone_from, timezone_to):
    datetime_str = f"{date_str} {time_str}"
    naive_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    localized_datetime = timezone_from.localize(naive_datetime)
    utc_datetime = localized_datetime.astimezone(timezone_to)
    new_date = utc_datetime.strftime("%Y-%m-%d")
    new_time = utc_datetime.strftime("%H:%M:%S")
    return new_date, new_time


# Main script

# Ensure the 'final' directory exists
if not os.path.exists("final"):
    os.makedirs("final")

# Specify the input directory
input_dir = "AI Revised 2/"

# Get list of files in the input directory
file_list = os.listdir(input_dir)

# Timezone definitions
cst = pytz.timezone("America/Chicago")
utc = pytz.timezone("UTC")

# Process each file in the directory
for filename in file_list:
    if filename.endswith(".json"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join("final", filename)

        # Read and load JSON data from the input file
        try:
            with open(input_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {input_path}: {e}")
            continue
        except IOError as e:
            print(f"Error reading file {input_path}: {e}")
            continue

        # Process each note in the JSON data
        for note in data.get("notes", []):
            # Convert start_time
            try:
                new_start_date, new_start_time = convert_time(
                    note["date"], note["start_time"], cst, utc
                )
                note["start_time"] = new_start_time
                if new_start_date != note["date"]:
                    note["date"] = new_start_date
            except KeyError as e:
                print(f"Warning in file {filename}: Missing key in note - {e}")
            except ValueError as e:
                print(
                    f"Warning in file {filename}: Invalid date or time format in note - {e}"
                )

            # Convert end_time
            try:
                new_end_date, new_end_time = convert_time(
                    note["date"], note["end_time"], cst, utc
                )
                note["end_time"] = new_end_time
                if new_end_date != note["date"]:
                    note["date"] = new_end_date
            except KeyError as e:
                print(f"Warning in file {filename}: Missing key in note - {e}")
            except ValueError as e:
                print(
                    f"Warning in file {filename}: Invalid date or time format in note - {e}"
                )

        # Write the modified data to the output file
        try:
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Processed and saved {output_path}")
        except IOError as e:
            print(f"Error writing to file {output_path}: {e}")
            continue
