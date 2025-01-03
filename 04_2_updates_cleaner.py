import json
import os

# Function to modify the JSON data
def modify_json(data):
    for board in data.get("data", {}).get("boards", []):
        for group in board.get("groups", []):
            for item in group.get("items_page", {}).get("items", []):
                # Filter the column_values to retain only 'Start Time' and 'End Time'
                item["column_values"] = [
                    col
                    for col in item.get("column_values", [])
                        if col.get("column", {}).get("title") in ["Manual units", "Units"]
                ]
    return data

boards = []
for root, dirs, files in os.walk("not-in-use/notes"):
    for file in files:
        if file.endswith(".json"):
            boards.append(os.path.join(root, file))

for board in boards:
    input_file = board
    output_file = board


    with open(input_file, "r") as file:
        json_data = json.load(file)

    # Modify the JSON data
    modified_data = modify_json(json_data)

    # Write the modified data back to a JSON file
    with open(output_file, "w") as file:
        json.dump(modified_data, file, indent=4)

    print(f"Modified JSON data has been written to {output_file}.")