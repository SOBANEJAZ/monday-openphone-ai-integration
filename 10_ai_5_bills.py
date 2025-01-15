from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import time

load_dotenv()
OPEN_AI_API = os.getenv("OPEN_AI_API")

client = OpenAI(api_key=OPEN_AI_API)

def analyze_issue(description):
    try:
        response = client.chat.completions.create(
            model="gpt-4-0613",  # Updated model name to match OpenAI's format
            messages=[{
                "role": "user",
                "content": f"{description}"
            }],
            functions=[{
                "name": "issue_analysis",
                "description": "Analyze severity and reason for each note and its units",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "notes_analysis": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "note_index": {
                                        "type": "integer",
                                        "description": "Index of the note starting from 0"
                                    },
                                    "billing_severity": {
                                        "type": "string",
                                        "enum": ["overbilled", "good"],
                                        "description": "Whether the billing is appropriate or overbilled"
                                    },
                                    "billing_reason": {
                                        "type": "string",
                                        "description": "Explanation for the billing assessment"
                                    },
                                    "billing_improved": {
                                        "type": "string",
                                        "description": "Improved version of the note or 'not required' if good"
                                    }
                                },
                                "required": ["note_index", "billing_severity", "billing_reason", "billing_improved"]
                            }
                        }
                    },
                    "required": ["notes_analysis"]
                }
            }],
            function_call={"name": "issue_analysis"}
        )

        result = json.loads(response.choices[0].message.function_call.arguments)
        return result
    except Exception as e:
        print(f"Error in analyze_issue: {str(e)}")
        return None

def process_files(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get list of all JSON files in the input folder
    json_files = [f for f in os.listdir(input_folder) if f.endswith(".json")]

    # Process each JSON file
    for filename in json_files:
        try:
            time.sleep(3)  # Rate limiting
            file_path = os.path.join(input_folder, filename)

            # Load data from the JSON file
            with open(file_path, "r") as f:
                data = json.load(f)

            # Prepare the description (your existing description string)
            description = f"""
                Your role is to analyze Session Notes, identify whether the added Units(manual_units) and notes are reseaonable.
            "You are a Session Notes Analyzer who analyzes notes for overbilling and good notes. You Label them either, 'overbilled' or 'good'. You provide a reason for each reason and Improves them by rewriting them. If the note does not has a problem and is written well, you output 'good'. Also for each note, you provide index for each note, starting from zero. 

            Comprehensive Identifier for Good Session Notes

            To build an AI that identifies good Session notes, the following framework integrates time-based billing correspondence, task categories (Direct Remote, Indirect Remote, Direct/In-Person), and quality standards. This ensures the evaluation considers both the service context and the depth/detail of the notes.

            General Criteria for Good Session Notes
            2.	Completeness: Includes all relevant information about:
            •	Purpose of the service.
            •	Actions performed by the writer.
            •	Outcomes and next steps.
            3.	Relevance: Focuses only on the services provided and avoids unrelated details.
            4.	Billing Alignment: Matches the level of detail and scope of the service with the amount billed:
            •	$17.17 (1 unit): Brief interaction or task.
            •	$34.34 (2 units): Moderate interaction with 2-3 tasks.
            •	$68.68 (4 units): Detailed, multi-step service.

            Category-Specific Criteria

            Direct Remote:
            •	Definition: Services delivered directly to the client remotely (e.g., via phone or video).
            •	Good Notes:
            •	Concisely summarize the purpose of the call and client concerns.
            •	Clearly describe the writer’s actions during and after the call (e.g., research, follow-up).
            •	Align the level of detail with the time billed:
            •	1 unit ($17.17): Example: “Received a call from the client about ADA concerns. Reassured client of follow-up. Reviewed ADA compliance documents and emailed the landlord.”
            •	4 units ($68.68): Example: “Conducted a 30-minute call discussing ADA concerns, followed by 30 minutes researching compliance laws. Drafted an email to the landlord and documented follow-up steps.”

            Indirect:
            •	Definition: Services provided without direct client interaction (e.g., email, research).
            •	Good Notes:
            •	Clearly document written communication (e.g., emails sent) and research efforts.
            •	Demonstrate logical progress toward resolving client concerns.
            •	Correspond with the billed amount:
            •	1 unit ($17.17): Example: “Composed an email to the property manager regarding ADA violations.”
            •	4 units ($68.68): Example: “Drafted a detailed email to the landlord about ADA issues. Spent 45 minutes compiling a list of affordable housing options across four platforms.”

            Direct/In-Person:
            •	Definition: Services provided in person with the client.
            •	Good Notes:
            •	Include detailed descriptions of in-person activities (e.g., completing forms, traveling).
            •	Record tangible outcomes (e.g., documents submitted, updates provided).
            •	Align with billed time:
            •	1 unit ($17.17): Example: “Met briefly to collect documents for a housing application.”
            •	4 units ($68.68): Example: “Spent an hour with the client completing a housing application, traveling to the Social Security office, and submitting documents at the leasing office.”


            Red Flags for Bad Session Notes
            1.	Overbilling:
            •	Notes are too vague for the amount billed (e.g., “$68.68 billed for a single phone call”).
            •	Example: “Reviewed ADA laws and sent an email.” (Insufficient for 4 units.)
            •	Example: “Sent a voicemail.” (Insufficient for 5 unit.)

            Guidelines for Improving Notes
            1.	Use the following guidelines to improve notes:
            - The improved note should estimate the same word count as the original note.
            - The improved note should be written in a way that is clear and easy to read.
            Example 1 of Original and Improved Note label marking:
            Original Note: HC had received a helpful email from the client's case worker with a list of towns that he is interested in. HC has looked into some of the possible dwellings in the suggested locations. HC will need to make a few calls to make sure the client is able to afford it. HC will also be looking into more tax-accredited housing. For now, HC will have an easier time finding housing for him.
            manual_units: "10"
            billing_severity: 'overbilled''
            billing_reason: The note describes basic research and planning activities that don't justify 10 units ($171.70). The activities described (reviewing an email, preliminary housing research, and planning future actions) would typically warrant 2-4 units maximum.
            The note lacks specific details about the actual time spent, number of properties researched, or concrete actions taken. Most content describes future plans rather than completed work.
            billing_improved: 
            Reviewed detailed email from client's case worker outlining preferred towns for housing search. Conducted extensive research of available housing options in target locations, focusing particularly on affordability and accessibility for client. Initial search identified several promising properties in preferred areas, though further verification of financial requirements is needed. Compiled comprehensive list of tax-credited housing opportunities in desired locations for additional consideration. 

            Created detailed action plan moving forward:
            • Follow up with property managers regarding specific income requirements and availability
            • Expand search of tax-credited housing options in surrounding areas
            • Schedule client meeting to review viable housing options and gather additional preferences

            Housing search has been streamlined based on case worker's location recommendations. Will continue focused search efforts within client's preferred towns while prioritizing affordable and tax-credited options that align with client's financial situation.
            Example 2 of Original and Improved Note and label marking:
            Original Note: No response from client yet HC will message him tomorrow to see if there has been any update about his application as HC hasn't received an email yet. During this time HC had been searching for other housing in Chisago County in case client doesn't get in as the property that client wanted HC to apply to is first come first served at that property.
            manual_units: "12"
            billing_severity: 'overbilled'
            billing_reason: "1. The activities described (checking for client response, planning to message tomorrow, and searching housing) don't justify 12 units ($212.4) of billing time. These tasks typically require less time and effort.
            2. The note lacks sufficient detail about the housing search process (how many properties were searched, what platforms were used, what specific criteria were considered) to warrant such high billing."
            billing_improved:
            Attempted to reach client regarding pending application status - no response received via email or messages. Conducted extensive housing search in Chisago County as a contingency plan, given the first-come-first-served nature of client's preferred property. Research identified several promising alternatives matching client's requirements, including Pine Ridge Apartments and Evergreen Commons. Created shortlist of backup options within client's budget range and accessibility needs. Will contact client tomorrow morning to check on primary application status and discuss alternative housing options if needed. Note: Current property remains first choice, but having backup options ready ensures client won't face housing delays if primary application falls through.

            Example 3 of Original and Improved Note and label marking:
            Oriignal Note: HC called two different numbers. First, HC called the client's number, which rang but was not answered, so HC left a voicemail. Next, HC called the girlfriend's number, but it was disconnected. Previously, the client's phone had been off, but this time it rang, so HC left a message asking the client to return the call upon receiving it.
            manual_units: "2"
            billing_severity: 'good'
            billing_reason: The level of detail matches the billing unit (2 unit for brief phone attempts), and includes relevant context about previous attempts ("Previously, the client's phone had been off").
            billing_improved: "not required"

            Note: The AI should output one of the following labels for each note:
            - Index(starting from 0), severity:good, reason, improved[just say "not required"] 
            - Index(starting from 0), severity:overbilled, reason, improved

            Json key:
            original note: "update_text_body"
            Units: "manual_units"
            **Session Notes**: {data['notes']}

            Make sure the structure of the response is as follows in this example:
            "notes_analysis": [
                {{
                    "note_index": 0,
                    "severity": "overbilled",
                    "reason": "The note is too vague for the amount billed. The note describes basic research and planning activities that don't justify 10 units ($171.70). The activities described (reviewing an email, preliminary housing research, and planning future actions) would typically warrant 2-4 units maximum. The note lacks specific details about the actual time spent, number of properties researched, or concrete actions taken. Most content describes future plans rather than completed work."
                }}
            ]
            """

            # Perform analysis
            analysis = analyze_issue(description)

            if analysis is None:
                print(f"Skipping {filename} due to analysis error")
                continue

            # Update the data with analysis results
            for i, note_analysis in enumerate(analysis.get("notes_analysis", [])):
                if i < len(data["notes"]):
                    try:
                        data["notes"][i].update({
                            "billing_severity": note_analysis.get("billing_severity", "unknown"),
                            "billing_reason": note_analysis.get("billing_reason", ""),
                            "billing_improved": note_analysis.get("billing_improved", "not required")
                        })
                    except Exception as e:
                        print(f"Error updating note {i} in {filename}: {str(e)}")

            # Save the updated data
            output_file_path = os.path.join(output_folder, filename)
            with open(output_file_path, "w") as f:
                json.dump(data, f, indent=2)

            print(f"Processed {filename} and saved to {output_file_path}")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    input_folder = "AI Revised 4"
    output_folder = "AI Revised 5"
    process_files(input_folder, output_folder)