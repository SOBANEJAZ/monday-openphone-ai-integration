from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
OPEN_AI_API = os.getenv("OPEN_AI_API")

client = OpenAI(api_key=OPEN_AI_API)


def analyze_issue(description):
    response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
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
                                    "severity": {
                                        "type": "string",
                                        "enum": ["low", "medium", "high", "good note"],
                                    },
                                    "reason": {"type": "string"},
                                },
                                "required": ["note_index", "severity", "reason"],
                            },
                        },
                    },
                    "required": ["notes_analysis"],
                },
            }
        ],
        function_call={"name": "issue_analysis"},
    )
    result = json.loads(response.choices[0].message.function_call.arguments)
    return result


# Specify the folder containing the JSON files
input_folder = "data/notes/filtered_notes/"
output_folder = "AI Revised"

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get list of all JSON files in the input folder
json_files = [f for f in os.listdir(input_folder) if f.endswith(".json")]

# Process each JSON file
for filename in json_files:
    file_path = os.path.join(input_folder, filename)

    # Load data from the JSON file
    with open(file_path, "r") as f:
        data = json.load(f)

    # Prepare the description
    description = f"""
    You are given session notes and corresponding call details and transcripts recorded by the Housing Coordinator. Your task is to analyze each note in the provided session notes and determine if there is a corresponding call session within 60 minutes of the start and end times of the note. Also, check if a transcript exists for the call.

    Follow these steps for each note:

    1. **Matching Call and Transcript**: 
       - Verify if there is a call session and transcript that corresponds to the note.
       - Compare the start and end times of the note with the call session times.
       - Calculate the time difference between the note and the transcript duration.

    2. **Severity Assessment**:
       - If the time difference is 5 minutes or less, mark the note as 'low' severity.
       - If the time difference is more than 10 minutes but less than or equal to 15 minutes, mark the note as 'medium' severity.
       - If the time difference exceeds 15 minutes, mark the note as 'high' severity.
       - If the time difference is exactly 1 or 2 minutes, mark it as a 'good note'.
       - If no transcript or time record is found for the note, mark it as 'high' severity.
       - If time record is found but no transcript, mark it as 'good note' severity, also in final response for this don't mention absence of transcript. Just compare time records.

    3. **Service Type Consideration**:
       - If the service provided is either Direct/In Person or Indirect, mark the note as 'good note' severity and do not verify call records and transcripts. Just tell reason that the service was in person so no need to verify call records and transcripts and in Indirect, verify call records if available and if they are not then mark it as good note. 
       - Verify call records and transcripts if the service is Direct Remote through a call, no call records or transcripts, mark it as 'high' severity.
       - Direct
         • Definition: Services provided in person with the client.
       - Indirect Remote
         • Definition: Services provided without direct client interaction (e.g., email, research).
       - Direct Remote
         • Definition: Services delivered directly to the client remotely (e.g., via phone or video).

    4. **Content Completeness**:
       - If a transcript exists but the note lacks important information from the transcript, mark it as 'medium' severity and provide a detailed reason.

    5. **Detailed Reasoning**:
       - For each note, provide a detailed reasoning for the severity level assigned. 
       - Explain your reasoning comprehensively for each assessment.

    Make sure to evaluate each note thoroughly, providing a severity level and an explanatory reason for every single note.
    Make sure that the reasoning is clear and and fully detailed around 3 lines or more.
    **Session Notes**: {data['notes']}
    **Call Transcripts**: {data['call_transcripts']}
    """

    # Perform analysis
    analysis = analyze_issue(description)

    # Update the data with analysis results
    for i, note_analysis in enumerate(analysis["notes_analysis"]):
        data["notes"][i]["severity"] = note_analysis["severity"]
        data["notes"][i]["reason"] = note_analysis["reason"]

    # Construct output file path
    output_file_path = os.path.join(output_folder, filename)

    # Save the updated data to a new JSON file
    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Processed {filename} and saved to {output_file_path}")
