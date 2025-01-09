from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
OPEN_AI_API = os.getenv("OPEN_AI_API")

client = OpenAI(api_key=OPEN_AI_API)


def analyze_issue(description):
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  # Updated to the latest available model
            messages=[{"role": "user", "content": f"{description}"}],
            functions=[
                {
                    "name": "issue_analysis",
                    "description": "Analyze severity and reason for each note based on transcripts",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "notes_analysis": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "note_index": {"type": "integer"},
                                        "start_severity": {
                                            "type": "string",
                                            "enum": ["Start Flagged", "Start Good"],
                                        },
                                        "end_severity": {
                                            "type": "string",
                                            "enum": ["End Flagged", "End Good"],
                                        },
                                        "start_reason": {"type": "string"},
                                        "end_reason": {"type": "string"},
                                    },
                                    "required": [
                                        "note_index",
                                        "start_severity",
                                        "end_severity",
                                        "start_reason",
                                        "end_reason",
                                    ],
                                },
                            },
                        },
                        "required": ["notes_analysis"],
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
        if "notes_analysis" not in result:
            raise ValueError("Missing notes_analysis in API response")

        for note in result["notes_analysis"]:
            required_fields = [
                "note_index",
                "start_severity",
                "end_severity",
                "start_reason",
                "end_reason",
            ]
            missing_fields = [field for field in required_fields if field not in note]
            if missing_fields:
                raise ValueError(f"Missing required fields in note: {missing_fields}")

        return result

    except Exception as e:
        print(f"Error in analyze_issue: {str(e)}")
        # Return a default structure in case of error
        return {"notes_analysis": []}


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
            You are an **Employee Time Checker**. Your task is to evaluate the accuracy of employee times based on the following sequence:
            - **Session Creation Time** -> **Start Time** -> **End Time** -> **Update Creation Time**.

            For each note in the **Session Notes**, you need to:
            1. Assign a severity (Good or Flagged) to the Start and End times.
            2. Provide a clear and detailed reason for your assessment based on the following criteria:

            ### 1. **Start Time vs. Session Creation Time**:
            - If the **Start Time** is more than 15 minutes before the **Session Creation Time**, mark it as **Flagged**.
            - If the **Start Time** is within 15 minutes before or anytime after the **Session Creation Time**, mark it as **Good**.

            ### 2. **End Time vs. Update Creation Time**:
            - If the **End Time** is before or within 15 minutes after the **Update Creation Time**, mark it as **Good**.
            - If the **End Time** is more than 15 minutes after the **Update Creation Time**, mark it as **Flagged**.


            ### Example Start Reason:
            - **Flagged Reason**: The **Start Time** was 31 minutes earlier than the **Session Creation Time**. The **Start Time** was 9:01 AM, and the **Session Creation Time** was 9:32 AM. Hence, the note is marked as Flagged due to the significant discrepancy.
            - **Good Reason**: The **Start Time** was hours after the **Session Creation Time**. The **Start Time** was 10:01 AM, and the **Session Creation Time** was 9:01 AM. Because the **Start Time** was after the **Session Creation Time**, the note is marked as Good.

            ### Example End Reason:
            - **Flagged Reason**: The **End Time** was 33 minutes after the **Update Creation Time**. The **End Time** was 10:02 AM, and the **Update Creation Time** was 10:35 AM. Hence, the note is marked as Flagged due to the significant discrepancy.
            - **Good Reason**: The **End Time** was hours before the **Update Creation Time**. The **End Time** was 11:02 AM, and the **Update Creation Time** was 12:02 AM. Because the **End Time** was before the **Update Creation Time**, the note is marked as Good.

            Use the 12-hour time format (e.g., 10:02 AM, 12:00 PM) in your responses.

            ### Value Map:
            - **Session Creation Time** = "session_creation_time"
            - **Start Time** = "start_time"
            - **End Time** = "end_time"
            - **Update Creation Time** = "update_creation_time"

            **Session Notes**: {data['notes']}
            """


            # Perform analysis
            analysis = analyze_issue(description)

            if not analysis["notes_analysis"]:
                print(f"Warning: No analysis results for {filename}")
                continue

            # Update the data with analysis results
            for note_analysis in analysis["notes_analysis"]:
                note_index = note_analysis["note_index"]
                if note_index < len(data["notes"]):
                    for field in [
                        "start_severity",
                        "start_reason",
                        "end_severity",
                        "end_reason",
                    ]:
                        if field in note_analysis:
                            data["notes"][note_index][field] = note_analysis[field]

            # Save the updated data to a new JSON file
            with open(output_file_path, "w") as f:
                json.dump(data, f, indent=2)

            print(f"Successfully processed {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue


if __name__ == "__main__":
    input_folder = "AI Revised"
    output_folder = "AI Revised 2"
    process_files(input_folder, output_folder)
