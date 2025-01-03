import json
import requests
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.getenv("AIRTABLE_API_KEY"))

table = api.table("appYvU5Req8gKzr7A", "tblUjWsTBe299fVF9")

table = table.all()

print(table)