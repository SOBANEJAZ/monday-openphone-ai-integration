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
                    "description": "Analyze severity and reason for each note based on Session Creation Time and Start Time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "time_analysis": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "note_index": {"type": "integer"},
                                        "start_severity": {
                                            "type": "string",
                                            "enum": ["Good", "Flagged"],
                                        },
                                        "start_reason": {"type": "string"},
                                    },
                                    "required": [
                                        "note_index",
                                        "start_severity",
                                        "start_reason",
                                        
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
                "start_severity",
                "start_reason",
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
            You are an **Employee Time Checker**. Your task is to evaluate the accuracy of employee added times based on the following sequence for each note:
            - First **Session Creation Time** and then **Start Time**. Make sure that this sequence is followed, if not then output the note as **Flagged**. If the Session Creation Time is before the Start Time within 20 minutes, then output the note as **Good**. If the Session Creation Time is 20 minutes or more before the Start Time, then output the note as **Flagged**.

            For each note in the **Session Notes**, you need to:
            1. Assign an Index to each note, starting from zero.
            1. Assign a severity (Good or Flagged) for each note.
            2. Provide a clear and detailed reason for your assessment based on the following criteria:

            ### 1. **Session Creation Time vs. Start Time**:
            - If the **Session Creation Time** is before the **Start Time**, mark it as **Good**.
            - If the **Session Creation Time** is after the **Start Time**, mark it as **Flagged**.
            - If Start Time is not provided, mark the note as **Flagged**.
            - Always use 12 Hour Time Format should be (e.g., 01:30 AM/PM).
            - Always provide the time difference between **Session Creation Time** and **Start Time** in the reason. The difference should be in format of **HH:MM**.

            ### Example Reasons:
            - **Good Reason**: The Session Creation Time was 13 minutes earlier than the Start Time. The Session Creation Time was 11:13 AM, and the Start Time was 11:26 AM. Therefore, the note is marked as Good due to the correct time entry.
            - **Flagged Reason**: The Session Creation Time was 31 minutes earlier than the Start Time. The Session Creation Time was 12:06 AM, and the Start Time was 12:37 AM. Therefore, the note is marked as Flagged due to the correct time entry. The Session Creation Time should be before the Start Time within 20 minutes.
            - **Flagged Reason**: The Session Creation Time was an hours after the Start Time. The Session Creation Time was 10:01 AM, and the Start Time was 9:01 AM. Because the Session Creation Time was after the Start Time, the note is marked as Flagged. The Session Creation Time should be before the Start Time within 20 minutes.

            Use the 12-hour time format (e.g., 10:02 AM, 12:00 PM) in your responses.
            Make sure you provide the correct severity and reason for each note and give each its index in the sequence(starting from zero).

            ### Value Map:
            - **Session Creation Time** = "session_creation_time"
            - **Start Time** = "start_time"

            **Session Notes**: {data['notes']}


            Steps to follow:
            1. Assign an Index to each note, starting from zero.
            2. Calculate the time difference between **Session Creation Time** and **Start Time** in minutes.
            3. If the Session Creation Time is before the Start Time within 20 minutes, then output the note as **Good**.
            4. If the Session Creation Time is 20 minutes or more before the Start Time, then output the note as **Flagged**.
            5. If the Start Time is not provided, mark the note as **Flagged**.
            6. If the Session Creation Time is after the Start Time, mark the note as **Flagged**.
            7. Output a clear and consice reason for the severity marked and use the example reasons to understand how to write the reason.
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
                        "start_severity",
                        "start_reason",
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
    input_folder = "AI Revised 1"
    output_folder = "AI Revised 2"
    process_files(input_folder, output_folder)
