import json


def process_calls(input_file, staff_file):
    # Load staff data
    with open(staff_file, "r") as f:
        staff_data = json.load(f)
    staff_numbers = {person["number"] for person in staff_data}

    # Load calls data
    with open(input_file, "r") as f:
        calls = json.load(f)

    # Process each call
    for call in calls:
        if call.get("call_transcript") and call["call_transcript"].get("data"):
            dialogue = call["call_transcript"]["data"]["dialogue"]

            # Create new conversation format
            formatted_transcript = {
                "conversation": [
                    {
                        "speaker": (
                            "Staff Member"
                            if entry["identifier"] in staff_numbers
                            else "Client"
                        ),
                        "message": entry["content"],
                    }
                    for entry in dialogue
                ]
            }

            # Replace old transcript with new format
            call["call_transcript"] = formatted_transcript

    # Save processed calls
    with open("data/reference/phone_details.json", "w") as f:
        json.dump(calls, f, indent=2)

    return calls


# Example usage
input_file = "data/reference/phone_details.json"
staff_file = "data/reference/init.json"
processed_data = process_calls(input_file, staff_file)
