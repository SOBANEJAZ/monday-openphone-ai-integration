import json
import requests
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

# Initialize the Airtable API
api = Api(os.getenv("AIRTABLE_API_KEY"))
table = api.table("appYvU5Req8gKzr7A", "tblUjWsTBe299fVF9")

# Get all the records from the Airtable
table = table.all()

table = json.dumps(table, indent=4)

print(table)