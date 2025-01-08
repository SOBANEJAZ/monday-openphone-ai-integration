import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()
api = os.getenv("MONDAY_API_KEY")


url = "https://api.monday.com/v2"

headers = {
    "Content-Type": "application/json",
    "Authorization": api,
}


query = """
query {
  boards (ids: 8139951792) {
    columns {
      id
      title
    }
  }
}
"""

payload = {"query": query}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    # Save response to a JSON file
    with open("_columns.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    print("Response saved to monday_response.json")
else:
    print("Failed to retrieve data. Status code:", response.status_code)


# ===============
# -----------------


import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()
api = os.getenv("MONDAY_API_KEY")


url = "https://api.monday.com/v2"

headers = {
    "Content-Type": "application/json",
    "Authorization": api,
}


query = """
query {
  boards (ids: 8139951792) {
    groups {
      title
      id
    }
  }
}
"""

payload = {"query": query}

response = requests.post(
    url, headers=headers, json=payload
)

# Step 5: Handle the response
if response.status_code == 200:
    data = response.json()
    # Extract and print the groups data
    boards = data.get("data", {}).get("boards", [])
    for board in boards:
        groups = board.get("groups", [])
        with open("_groups.json", "w") as f:
            json.dump(groups, f, indent=4)
        for group in groups:
            print(f"Title: {group['title']}, ID: {group['id']}")


else:
    # If something went wrong, print the error message
    print(f"Error: {response.status_code}")
    print(response.text)


# --------------

import json

# Load init.json data
with open("data/reference/init.json", "r") as f:
    init_data = json.load(f)

# Load _groups.json data
with open("_groups.json", "r") as f:
    groups_data = json.load(f)

# Create a mapping from title to id
title_to_id = {group["title"]: group["id"] for group in groups_data}

# Update each item in init_data with group_name if it matches
for item in init_data:
    staff_member = item["Staff Member"]
    if staff_member in title_to_id:
        item["group_name"] = title_to_id[staff_member]
    else:
        # Optional: handle members without a matching group
        print(f"No matching group found for Staff Member: {staff_member}")

# Save the updated init.json
with open("data/reference/init.json", "w") as f:
    json.dump(init_data, f, indent=4)

# ----------------
# ==================


import json
import os

# Step 1: Read init.json and create mapping
with open("data/reference/init.json", "r") as f:
    init_data = json.load(f)

board_id_to_group = {item["Board_id"]: item["group_name"] for item in init_data}

# Step 2: Set directories
final_dir = "Final"
output_dir = "Output"

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Step 3: Process each file in Final directory
for filename in os.listdir(final_dir):
    if filename.endswith(".json"):
        # Extract Board_id from filename
        board_id = filename[:-5]  # Remove '.json' extension
        group_name = board_id_to_group.get(board_id)
        if group_name:
            # Read the file content
            with open(os.path.join(final_dir, filename), "r") as f:
                data = json.load(f)
            # Add group_name to each notes item
            notes_list = data.get("notes", [])
            for note in notes_list:
                note["group_name"] = group_name
            # Save the modified content to Output directory
            with open(os.path.join(output_dir, filename), "w") as f:
                json.dump(data, f, indent=4)
            print(f"Processed and saved {filename}")
        else:
            print(f"No matching group_name for {filename}")
