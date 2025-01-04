import json

# Corrected JSON data
json_data = """
{
  "data": {
    "boards": [
      {
        "groups": [
          {
            "title": "Data",
            "id": "topics",
            "items_page": {
              "cursor": null,
              "items": [
                {
                  "id": "8160493734",
                  "name": "Kendahl Kirk",
                  "updates": [],
                  "column_values": [
                    {
                      "column": {
                        "title": "Board ID"
                      },
                      "value": "\"6324705748\""
                    },
                    {
                      "column": {
                        "title": "Phone Number"
                      },
                      "value": "\"+16516158915\""
                    }
                  ]
                },
                {
                  "id": "8160505513",
                  "name": "Hind Elzain",
                  "updates": [],
                  "column_values": [
                    {
                      "column": {
                        "title": "Board ID"
                      },
                      "value": "\"6719676064\""
                    },
                    {
                      "column": {
                        "title": "Phone Number"
                      },
                      "value": "\"+16516153230\""
                    }
                  ]
                },
                {
                  "id": "8160506255",
                  "name": "Ubah Ahmed",
                  "updates": [],
                  "column_values": [
                    {
                      "column": {
                        "title": "Board ID"
                      },
                      "value": "\"4482658418\""
                    },
                    {
                      "column": {
                        "title": "Phone Number"
                      },
                      "value": "\"+16126822100\""
                    }
                  ]
                },
                {
                  "id": "8160506531",
                  "name": "Abdirahman Ibrahim",
                  "updates": [],
                  "column_values": [
                    {
                      "column": {
                        "title": "Board ID"
                      },
                      "value": "\"7217305033\""
                    },
                    {
                      "column": {
                        "title": "Phone Number"
                      },
                      "value": "\"+16516615910\""
                    }
                  ]
                }
              ]
            }
          }
        ]
      }
    ]
  }
}
"""

# Load the JSON data
import os
dir = 'initial_data/data.json'
with open (dir, 'r') as f:
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

# Print the result
print(json.dumps(result, indent=2))
