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
                "name": "service_analysis",
                "description": "analyze the note and check if the service line and service type are added correctly",
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
        function_call={"name": "service_analysis"},
    )
    result = json.loads(response.choices[0].message.function_call.arguments)
    return result


# Specify the folder containing the JSON files
input_folder = "AI Revised 3"
output_folder = "AI Revised 4"

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
    You are a Session Notes Service Line and Service Type Analyzer.
    Your goal is to analyze session notes and verify whether the added service line and type match the note. If the note and service line and service type do not match, mark the note as 'Flagged' and output a concise and clear reason for it.  Provide an index for each note, starting from zero.
    If the note matches the service line and service type, mark the note as 'Good'. Provide an index for each note, starting from zero.

    Here are the details for identifying the service type and line:

    Service Type:
    - 1: Transitioning
    - 2: Sustaining
    - 3: Non-billable

    Service Lines in respect to their service type:

    "Service_Type": "Housing Transition",
    "Covered_Services": [
        "Developing a housing transition plan",
          "Supporting the person in applying for benefits to afford their housing, including helping the person determine which benefits they may be eligible for",
          "Assisting the person with the housing search and application process",
          "Assisting the person with tenant screening and housing assessments",
          "Providing transportation with the person receiving services present and discussing housing-related issues",
          "Helping the person understand and develop a budget",
          "Helping the person understand and negotiate a lease",
          "Helping the person meet and build a relationship with a prospective landlord",
          "Promoting/supporting cultural practice needs and understandings with prospective landlords, property managers",
          "Helping the person find funding for deposits",
          "Helping the person organize their move",
          "Researching possible housing options for the person",
          "Contacting possible housing options for the person",
          "Identifying resources to pay for deposits or home goods",
          "Identifying resources to cover moving expenses",
          "Completing housing applications on behalf of the service recipient",
          "Working to expunge records or access reasonable accommodations",
          "Identifying services and benefits that will support the person with housing instability",
          "Ensuring the new living arrangement is safe for the person and ready for move-in",
          "Arranging for adaptive house-related accommodations required by the person",
          "Arranging for assistive technology required by the person"
    ]

    "Service_Type": "Housing Sustaining",
    "Covered_Services": [
       "Developing, updating, and modifying the housing support and crisis/safety plan on a regular basis",
         "Preventing and early identification of behaviors that may jeopardize continued housing",
         "Educating and training on roles, rights, and responsibilities of the tenant and property manager",
         "Transportation with the person receiving services present and discussing housing-related issues",
         "Promoting/supporting cultural practice needs and understandings with landlords, property managers, and neighbors",
         "Coaching to develop and maintain key relationships with property managers and neighbors",
         "Advocating with community resources to prevent eviction when housing is at risk and maintain the person’s safety",
         "Assistance with the housing recertification processes",
         "Continued training on being a good tenant, lease compliance, and household management",
         "Supporting the person to apply for benefits to retain housing",
         "Supporting the person to understand and maintain/increase income and benefits to retain housing",
         "Supporting the building of natural housing supports and resources in the community, including building supports and resources related to a person’s culture and identity",
         "Working with property manager or landlord to promote housing retention",
         "Arranging for assistive technology",
         "Arranging for adaptive house-related accommodations"
    ]

    "Service_Type": "Non-billable",
    "Covered_Services": [
        "Staff Meeting",
        "Intake Meeting",
        "Others"
    ]

    If the service type and service line are not added correctly, mark the note as 'Flagged' and output a concise and clear reason for it. If the note matches the service line and service type, mark the note as 'Good'. For each note, provide an index starting from zero.
    - If the service line matches the note but the service type doesn't, mark the note as 'Flagged' and output a concise and clear reason for it, and vice versa.
    - If either the service line or service type does not exist or is not added, mark the note as 'Flagged'
    - Go through each and make sure the reponses are in structured format.

    **Session Notes**: {data['notes']}

    Key for analyzing the parts of JSON:
    Note Session: "update_text_body",
    Service Line: "service_line",
    Service Type: "service_type",

    Examples:

    Good Example:
    Note Session: "I assisted the client in completing their housing application today.",
    Service Line: "Assisting the person with the housing search and application process",
    Service Type: "Housing Transition",

    AI response in json format:
    "index": 0,
    "label": "Good",
    "reason": "In the note, Assistance of client in completing their housing application matches the added Service Line and Service type.",

    Flagged Example:
    Note Session: "I met the client in person and we helped in meet the landlord",
    Service Line: "Helping the person meet and build a relationship with a prospective landlord",
    Service Type: "Housing Sustaining",
    AI response in json format:
    "index": 1,
    "label": "Flagged",
    "reason": "The note indicates helping the person meet and build a relationship with a prospective landlord, but the added service line is Housing Sustaining. The note should be marked as Flagged, due to the mismatch between the added service line and servie type. The service type should be updated to Housing Transition.""
    
    Flagged Example:
    Note Session: "We had a staff meeting to discuss housing options for the client.",
    Service Line: "Assisting the person with the housing search and application process",
    Service Type: "Housing Transition",
    
    Make sure the structure of the response is as follows in this example:
    "notes_analysis": [
        {{
            "note_index": 0,
            "severity": "Flagged",
            "reason": "The note indicates helping the person meet and build a relationship with a prospective landlord, but the added service line is Housing Sustaining. The note should be marked as Flagged, due to the mismatch between the added service line and servie type. The service type should be updated to Housing Transition."
        }}
    ]
    """


    # Perform analysis
    analysis = analyze_issue(description)

    # Update the data with analysis results
    for i, note_analysis in enumerate(analysis["notes_analysis"]):
        data["notes"][i]["service_severity"] = note_analysis["severity"]
        data["notes"][i]["service_reason"] = note_analysis["reason"]

    # Construct output file path
    output_file_path = os.path.join(output_folder, filename)

    # Save the updated data to a new JSON file
    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Processed {filename} and saved to {output_file_path}")
