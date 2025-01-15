from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()
OPEN_AI_API = os.getenv("OPEN_AI_API")

client = OpenAI(api_key=OPEN_AI_API)


def analyze_issue(description):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-2024-11-20",  # Updated to the latest available model
            messages=[{"role": "user", "content": f"{description}"}],
            functions=[
                {
                    "name": "issue_analysis",
                    "description": "Analyze severity and reason for each note based on Session Update Time and End Time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "time_analysis": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "note_index": {"type": "integer"},
                                        "end_severity": {
                                            "type": "string",
                                            "enum": ["Good", "Flagged"],
                                        },
                                        "end_reason": {"type": "string"},
                                    },
                                    "required": [
                                        "note_index",
                                        "end_severity",
                                        "end_reason",
                                    ],
                                },
                            },
                        },
                        "required": ["time_analysis"],
                    },
                }
            ],
            function_call={"name": "issue_analysis"},
        )

        # Parse and validate the response
        if not response.choices or not response.choices[0].message.function_call:
            raise ValueError("Invalid response format from OpenAI API")

        result = json.loads(response.choices[0].message.function_call.arguments)

        # Validate the result structure
        if "time_analysis" not in result:
            raise ValueError("Missing time_analysis in API response")

        for note in result["time_analysis"]:
            required_fields = [
                "note_index",
                "end_severity",
                "end_reason",
            ]
            missing_fields = [field for field in required_fields if field not in note]
            if missing_fields:
                raise ValueError(f"Missing required fields in note: {missing_fields}")

        return result

    except Exception as e:
        print(f"Error in analyze_issue: {str(e)}")
        # Return a default structure in case of error
        return {"time_analysis": []}


def process_files(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get list of all JSON files in the input folder
    json_files = [f for f in os.listdir(input_folder) if f.endswith(".json")]

    for filename in json_files:
        try:
            file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

            # Load data from the JSON file
            with open(file_path, "r") as f:
                data = json.load(f)

            # Prepare the description
            description = f"""
            You are an **Employee Time Checker**. Your task is to evaluate the accuracy of employee added times based on the following sequence:
            First **Update Creation Time** and then **End Time**. Make sure that this sequence is followed, if not then mark the note as **Flagged**.  If the Update Creation Time is before the End Time, then output the note as **Good**.

            For each note in the **Session Notes**, you need to:
            1. Assign an Index to each note, starting from zero.
            1. Assign a severity (Good or Flagged) for each note.
            2. Provide a clear and detailed reason for your assessment based on the following criteria:

            ### 2. **End Time vs. Update Creation Time**:
            - If the **Update Creation Time** is before or at the **End Time**, mark it as **Good**.
            - If the **Update Creation Time** is after the **End Time**, mark it as **Flagged**.
            - If the **End Time** is not provided, mark it as **Flagged**.
            - Always use 12 Hour Time Format should be (e.g., 01:30 AM/PM).
            - Always provide the time difference between **Update Creation Time** and **End Time** in the reason. The difference should be in format of **HH:MM**.


            ### Example End Reason:
            - **Good Reason**: The Update Creation Time was hours before the End Time. The Update Creation Time was 11:02 AM, and the **End Time** was 12:02 AM. Because the Update Creation Time was before the End Time, the note is marked as Good.
            - **Flagged Reason**: The Update Creation Time was 33 minutes after the End Time. The End Time was 10:02 AM, and the Update Creation Time was 10:35 AM. Hence, the note is marked as Flagged due to the significant discrepancy.

            Use the 12-hour time format (e.g., 10:02 AM, 12:00 PM) in your responses.
            Make sure you provide the correct severity and reason for each note and give each its index in the sequence(starting from zero).

            ### Value Map:
            - **Update Creation Time** = "update_creation_time"
            - **End Time** = "end_time"

            **Session Notes**: {data['notes']}


            Steps to follow:
            1. Assign an Index to each note, starting from zero.
            2. Calculate the time difference between **Update Creation Time** and **End Time** in minutes.
            3. If the Update Creation Time is before the End Time, then output the note as **Good**.
            4. If the Update Creation Time is after the End Time, then output the note as **Flagged**.
            5. If the End Time is not provided, mark the note as **Flagged**.
            6. Output a clear and consice reason for the severity marked and use the example reasons to understand how to write the reason.

            Make sure the structure of the response is as follows in this example:
            "notes_analysis": [
                {{
                    "note_index": 0,
                    "severity": "Good",
                    "reason": "The Update Creation Time was 13 minutes earlier than the End Time. The Update Creation Time was 11:13 AM, and the End Time was 11:26 AM. Therefore, the note is marked as Good due to the correct time entry."
                }}
            ]
            """

            # Perform analysis
            analysis = analyze_issue(description)

            if not analysis["time_analysis"]:
                print(f"Warning: No analysis results for {filename}")
                continue

            # Update the data with analysis results
            for note_analysis in analysis["time_analysis"]:
                note_index = note_analysis["note_index"]
                if note_index < len(data["notes"]):
                    for field in [
                        "end_severity",
                        "end_reason",
                    ]:
                        if field in note_analysis:
                            data["notes"][note_index][field] = note_analysis[field]

            # Save the updated data to a new JSON file
            with open(output_file_path, "w") as f:
                json.dump(data, f, indent=2)

            print(f"Successfully processed {filename}")
            time.sleep(2)  # Add a delay to avoid rate limiting

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue


if __name__ == "__main__":
    input_folder = "AI Revised 2"
    output_folder = "AI Revised 3"
    process_files(input_folder, output_folder)
