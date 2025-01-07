import os
import time
import json
import requests
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Any
from requests.exceptions import RequestException

boards = [8159897010]

for board in boards:
    print(f"Fetching data for board {board}...")
    # Load API key from .env file
    load_dotenv()
    API_KEY = os.getenv("MONDAY_API_KEY")
    url = "https://api.monday.com/v2"
    headers = {
        "Content-Type": "application/json",
        "Authorization": API_KEY,
    }

    def fetch_items_from_board(board_id: int) -> List[str]:
        """Fetch all items from a specified board."""
        query = (
            """
        query {
            boards(ids: %d) {
                groups {
                    title
                    id
                    items_page(limit: 400) {
                        cursor
                        items {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
            % board_id
        )

        response = requests.post(url, json={"query": query}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Save response to a JSON file
            with open("monday_response.json", "w") as json_file:
                json.dump(data, json_file, indent=4)

            # Extract item IDs
            item_ids = []
            for board in data.get("data", {}).get("boards", []):
                for group in board.get("groups", []):
                    items = group.get("items_page", {}).get("items", [])
                    for item in items:
                        item_ids.append(item.get("id"))
            return item_ids
        return []

    def make_request_with_retry(
        query: str,
        variables: dict,
        batch_num: int,
        max_retries: int = 3,
        initial_delay: float = 1.0,
    ) -> Tuple[dict, bool]:
        """Make a request with retry logic and exponential backoff."""
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json={"query": query, "variables": variables},
                    headers=headers,
                    timeout=30,
                )

                print(f"Batch {batch_num} - Attempt {attempt + 1}:")
                print(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    response_data = response.json()

                    if "errors" in response_data:
                        print(f"GraphQL Errors in batch {batch_num}:")
                        print(json.dumps(response_data["errors"], indent=2))

                        error_messages = [
                            error.get("message", "").lower()
                            for error in response_data.get("errors", [])
                        ]
                        if any(
                            "complexity" in msg or "limit" in msg
                            for msg in error_messages
                        ):
                            print(
                                f"Detected complexity/limit error in batch {batch_num}"
                            )
                            return response_data, False

                        if attempt < max_retries - 1:
                            time.sleep(delay)
                            delay *= 2
                            continue
                        return response_data, False

                    items = response_data.get("data", {}).get("items", [])
                    if not items:
                        print(f"Warning: Batch {batch_num} returned no items")
                        print("Response data:", json.dumps(response_data, indent=2))

                    return response_data, True

                if response.status_code == 429:
                    print(
                        f"Rate limited on batch {batch_num}. Waiting {delay} seconds..."
                    )
                    time.sleep(delay)
                    delay *= 2
                    continue

                print(
                    f"Unexpected status code {response.status_code} on batch {batch_num}"
                )
                print(f"Response: {response.text}")

                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue

            except RequestException as e:
                print(
                    f"Request failed on batch {batch_num}, attempt {attempt + 1}: {str(e)}"
                )
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue

        return {"data": {"items": []}}, False

    def fetch_updates_in_batches(item_ids: List[str], batch_size: int = 25) -> dict:
        """Fetch updates for items in batches with retry logic and rate limiting."""
        all_updates = {"data": {"items": []}}
        successful_count = 0

        for i in range(0, len(item_ids), batch_size):
            batch = item_ids[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = -(-len(item_ids) // batch_size)
            print(
                f"\nProcessing batch {batch_num} of {total_batches} (Items {i+1}-{min(i+batch_size, len(item_ids))})"
            )

            updates_query = """
            query GetItemUpdates($itemIds: [ID!]!) {
                items(ids: $itemIds) {
                    id
                    name
                    updates {
                        id
                        text_body
                        created_at
                        updated_at 
                    }
                    column_values {
                        column {
                            title
                        }
                        value
                    }
                }
            }
            """

            variables = {"itemIds": list(map(str, batch))}

            batch_data, success = make_request_with_retry(
                updates_query, variables, batch_num
            )

            if success and batch_data.get("data", {}).get("items"):
                received_items = batch_data["data"]["items"]
                all_updates["data"]["items"].extend(received_items)
                successful_count += len(received_items)
                print(
                    f"Successfully retrieved {len(received_items)} items in this batch"
                )
            else:
                print(f"Failed to retrieve any items in batch {batch_num}")

            if i + batch_size < len(item_ids):
                time.sleep(1.5)

        return all_updates, successful_count

    def create_updates_dictionary(
        updates_data: dict,
    ) -> Tuple[Dict[str, list], Dict[str, list]]:
        """Create dictionaries of updates and column values indexed by item ID."""
        try:
            updates_dict = {}
            columns_dict = {}

            for item in updates_data.get("data", {}).get("items", []):
                if "id" in item:
                    item_id = item["id"]
                    if "updates" in item:
                        updates_dict[item_id] = item["updates"]
                    if "column_values" in item:
                        columns_dict[item_id] = item["column_values"]

            return updates_dict, columns_dict
        except (KeyError, AttributeError) as e:
            print(f"Error processing data: {e}")
            raise

    def update_items(
        data: Any, updates_by_id: Dict[str, list], columns_by_id: Dict[str, list]
    ) -> None:
        """Recursively update items with their corresponding updates and column values."""
        if isinstance(data, dict):
            if "items" in data:
                for item in data.get("items", []):
                    if "id" in item:
                        item_id = item["id"]
                        if item_id in updates_by_id:
                            item["updates"] = updates_by_id[item_id]
                        if item_id in columns_by_id:
                            item["column_values"] = columns_by_id[item_id]

            for value in data.values():
                update_items(value, updates_by_id, columns_by_id)
        elif isinstance(data, list):
            for item in data:
                update_items(item, updates_by_id, columns_by_id)

    def merge_responses(monday_data: dict, updates_data: dict) -> dict:
        """Merge the Monday data with updates and column values data."""
        try:
            # Create updates and columns dictionaries
            updates_by_id, columns_by_id = create_updates_dictionary(updates_data)

            # Create a copy of monday_data to avoid modifying the original
            merged_data = monday_data.copy()

            # Update the copied data with updates and column values
            update_items(merged_data, updates_by_id, columns_by_id)

            return merged_data
        except Exception as e:
            print(f"Error merging responses: {e}")
            raise

    def main():
        board_id = board
        item_ids = fetch_items_from_board(board_id)
        print(f"Found {len(item_ids)} items")

        all_updates, successful_count = fetch_updates_in_batches(item_ids)

        with open("item_updates.json", "w") as updates_file:
            json.dump(all_updates, updates_file, indent=4)

        print("\nFinal Summary:")
        print(f"Total items: {len(item_ids)}")
        print(f"Successfully processed: {successful_count}")
        print(f"Success rate: {(successful_count/len(item_ids))*100:.2f}%")

    def load_json_file(filename: str) -> dict:
        """Load and validate a JSON file."""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"Error: {filename} not found")
            raise
        except json.JSONDecodeError:
            print(f"Error: {filename} contains invalid JSON")
            raise

    def merger():
        print("Loading JSON files...")
        monday_data = load_json_file("monday_response.json")
        updates_data = load_json_file("item_updates.json")

        print("Merging responses...")
        merged_data = merge_responses(monday_data, updates_data)

        print("Saving merged data...")
        with open(f"data.json", "w") as f:
            json.dump(merged_data, f, indent=2)

        print("Successfully created merged data file")

        total_items = sum(
            len(group.get("items_page", {}).get("items", []))
            for board in merged_data.get("data", {}).get("boards", [])
            for group in board.get("groups", [])
        )

        total_updates = sum(
            len(item.get("updates", []))
            for board in merged_data.get("data", {}).get("boards", [])
            for group in board.get("groups", [])
            for item in group.get("items_page", {}).get("items", [])
            if "updates" in item
        )

        total_columns = sum(
            len(item.get("column_values", []))
            for board in merged_data.get("data", {}).get("boards", [])
            for group in board.get("groups", [])
            for item in group.get("items_page", {}).get("items", [])
            if "column_values" in item
        )

        print("\nMerge Statistics:")
        print(f"Total items processed: {total_items}")
        print(f"Total updates merged: {total_updates}")
        print(f"Total column values merged: {total_columns}")

        
        print("\nMerging complete!")

    if __name__ == "__main__":
        main()
        merger()


# # Load the JSON data
dir = "data.json"
print("structuring the data")
with open(dir, "r") as f:
    data = json.load(f)

# Initialize an empty list for the new structure
result = []

# Iterate through each item in the items list
for item in data["data"]["boards"][0]["groups"][0]["items_page"]["items"]:
    staff_member = item["name"]
    board_id = None
    number = None
    for column_value in item["column_values"]:
        if column_value["column"]["title"] == "Board ID":
            board_id = column_value["value"].strip('"')
        elif column_value["column"]["title"] == "Phone Number":
            number = column_value["value"].strip('"')
    # Create a dictionary with the desired keys and append to the result list
    result.append(
        {"Staff Member": staff_member, "Board_id": board_id, "number": number}
    )
with open("data/reference/staff_info.json", "w") as f:
    json.dump(result, f, indent=2)
print("structuring complete")
print("\nCleaning up directory...")
os.remove("monday_response.json")
os.remove("item_updates.json")
os.remove("data.json")
print("Successfully cleaned up directory")
print("All operations completed successfully!")
print("Initial data is ready for use.")


# ---------------------


import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Get the API key from the environment
OPENPHONE_API_KEY = os.getenv("OPENPHONE_API_KEY")


headers = {
    "Authorization": OPENPHONE_API_KEY,
}

raw_data = requests.get(
    "https://api.openphone.com/v1/phone-numbers", headers=headers
).json()

with open("data/reference/call_ids.json", "w") as f:
    extracted_data = []
    for item in raw_data["data"]:
        extracted_item = {
            "id": item["id"],
            "name": item["name"],
            "number": item["number"],
        }
        extracted_data.append(extracted_item)
    json.dump({"data": extracted_data}, f, indent=4)


# ---------------------

import json

# Load the first JSON file
with open("data/reference/call_ids.json", "r") as f:
    first_json = json.load(f)

# Load the second JSON file
with open("data/reference/staff_info.json", "r") as f:
    second_json = json.load(f)

# Create a mapping from number to id from the first JSON
number_to_id = {item["number"]: item["id"] for item in first_json["data"]}

# Iterate through the second JSON and add the id if the number matches
for item in second_json:
    number = item["number"]
    if number in number_to_id:
        item["id"] = number_to_id[number]

# Save or print the modified second JSON
with open("data/reference/init.json", "w") as f:
    json.dump(second_json, f, indent=4)

os.remove("data/reference/call_ids.json")
os.remove("data/reference/staff_info.json")

print("Reference data is ready for use.")
