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
                "name": "columns_analysis",
                "description": "analyze the note all the required columns are filled or not",
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
                                        "enum": ["Good", "Flagged"],
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
        function_call={"name": "columns_analysis"},
    )
    result = json.loads(response.choices[0].message.function_call.arguments)
    return result


# Specify the folder containing the JSON files
input_folder = "AI Revised 5"
output_folder = "AI Revised 6"

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
    You are Columns Checker and you verify whether all the required columns are filled by the staff member or not.
    If even one column is not filled, mark the note as 'Flagged' and output a concise and clear reason for it.  Provide an index for each note, starting from zero.
    If the note contains all the required columns, mark the note as 'Good'. Provide an index for each note, starting from zero.

    Here are the columns to look for in the json file:
    Start Time: "start_time",
    End Time: "end_time",
    Units: "manual_units",
    Service Type: "service_type"
    Provided as: "provided_as"
    Service Line: "service_line"
    Session Status: "session_status"
    If any of the above values is null or not exists, mark the note as 'Flagged' and output a concise and clear reason for it. Also mark it Flagged, if the Session status is either in-progress or not added. If all the column values exists, mark the note as 'Good'. For each note, provide an index starting from zero. Don't verify other values else then those that are mentioned above.
    

    The AI should output one of the following labels for each note:
    - Index, Good, reason,
    - Index, Flagged, reason

    **Session Notes**: {data['notes']}

    Examples:

    Good Example:
    "item_name": "session 4",
      "item_id": "8193469458",
      "session_creation_time": "2025-01-08 11:38:03",
      "update_creation_time": "2025-01-08 13:13:08",
      "date": "2025-01-08",
      "start_time": "11:14:00",
      "end_time": "13:20:35",
      "manual_units": "\"8\"",
      "service_type": "Transitioning",
      "provided_as": "indirect",
      "service_line": "Identifying services and benefits that will support the person with housing instability",
      "session_status": "Completed",
      "signature": null,
      "update_text_body": "HC has still not been able to contact the client as of yet. HC has sent gone through the client files to find a Emergency contact number. HC had came across a number for the client which seemed to be their mothers contact, but due to the client birth year it has left HC a bit confused. HC still tried to contact this number but was sent to voicemail. HC has requested for a separate contact number of the client to be sent over if the client does have a new number or someone who the client may be saying with. HC will stop by client current address when finishing a meeting later in the day.",
      "group_title": "Tony Holtgren 3/5/2025: MA",
      "transcript_severity": "good note",
      "transcript_reason": "Although the service was 'indirect,' call records were unavailable. The note was marked 'good note' because the service does not require direct interaction, prioritizing document completeness.",
      "start_severity": "Flagged",
      "start_reason": "The Session Creation Time (11:38 AM) was 24 minutes after the Start Time (11:14 AM).",
      "end_severity": "Good",
      "end_reason": "The Update Creation Time was 7 minutes before the End Time. The Update Creation Time was 01:13 PM, and the End Time was 01:20 PM. Because the Update Creation Time was before the End Time, the note is marked as Good.",
      "service_severity": "Flagged",
      "service_reason": "The note mentions HC attempting contact and coordinating emergency contacts with the client. This does not align with the 'Housing Transition' covered service 'Identifying services that support housing instability,' indicating a service mismatch.",
      "billing_severity": "overbilled",
      "billing_reason": "The tasks accomplished do not seem to justify the 8 units of service billed. The activities described, like attempts to contact the client and searching through files, are relatively simple and should not require this much billed time. The description of these activities is also quite vague, making it hard to assess whether they indeed required such extensive effort.",
      "billing_improved": "I dedicated this session to attempting contact with the client and getting an update on their housing situation. Despite my attempts, I was unable to reach the client directly. I meticulously searched through the client's files, coming across an emergency contact number. Immediate efforts to reach this contact were unsuccessful, but I left a detailed voicemail inquiring about the client's housing status. In the meantime, I will keep exploring backup housing options in Chisago County."

    AI response:
    "index": 0,
    "label": "Good",
    "reason": "All the columns are filled, therefore the note is marked as good",

    Flagged Example:
    "item_name": "Session 2",
      "item_id": "8192434037",
      "session_creation_time": "2025-01-08 10:19:43",
      "update_creation_time": "2025-01-08 11:36:51",
      "date": "2025-01-08",
      "start_time": "09:00:45",
      "end_time": "11:13:33",
      "manual_units": null,
      "service_type": "Sustaining",
      "provided_as": "Direct Remote",
      "service_line": "Educating and training on roles, rights, and responsibilities of the tenant and property manager",
      "session_status": "Completed",
      "signature": null,
      "update_text_body": "after the conversation with the client yesterday HC has started looking into some possible areas that the client could move to after hearing their situation with the landlords age and health. HC is currently looking at HB101 or cash assistance but is working towards getting the client on section 8. HC has some ideas on areas that the client could possibly stay at and HC has reached out to some connections about the housing situation in the client current home county. HC has also prepared a remote unit extension form and is in the process of sending it out to the client currently",
      "group_title": "Lynn Coury 3/25/2025: MA",
      "transcript_severity": "high",
      "transcript_reason": "The service was categorized as 'Direct Remote,' indicating call and transcript verification is required. No call records matched the note's start and end time, resulting in a 'high' severity due to absence of corresponding call data.",
      "start_severity": "Flagged",
      "start_reason": "The Session Creation Time (10:19 AM) was 1 hour and 19 minutes after the Start Time (09:00 AM).",
      "end_severity": "Flagged",
      "end_reason": "The Update Creation Time was 23 minutes after the End Time. The End Time was 11:13 AM, and the Update Creation Time was 11:36 AM. Hence, the note is marked as Flagged due to the discrepancy.",
      "service_severity": "Flagged",
      "service_reason": "The note describes HC researching and applying for housing-related assistance options like Section 8, which corresponds to the 'Housing Transition' service type and covered services like 'Researching possible housing options for the person,' but the incorrect 'Sustaining' service type was used.",
      "billing_severity": "overbilled",
      "billing_reason": "The note describes activities such as researching housing options, reaching out to connections, and preparing documents. However, it does not provide enough detail about these activities to justify the 10 units billed. Moreover, the service type marked as 'Sustaining' does not align with the activities described, indicating a potential service mismatch.",
      "billing_improved": "Today, I devoted my attention to researching suitable housing options for the client. I considered factors such as accessibility and affordability, targeting those in the client's preferred areas. I reached out to professional contacts for insights about the housing situation in the client's current county. Additionally, I prepared a remote unit extension form, which is in the process of being sent to the client."
    AI response:
    "index": 1,
    "label": "Flagged",
    "reason": "The Units are not added by the staff member, and due to this the note is being marked as Flagged."
    """


    # Perform analysis
    analysis = analyze_issue(description)

    # Update the data with analysis results
    for i, note_analysis in enumerate(analysis["notes_analysis"]):
        data["notes"][i]["columns_severity"] = note_analysis["severity"]
        data["notes"][i]["columns_reason"] = note_analysis["reason"]

    # Construct output file path
    output_file_path = os.path.join(output_folder, filename)

    # Save the updated data to a new JSON file
    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Processed {filename} and saved to {output_file_path}")
