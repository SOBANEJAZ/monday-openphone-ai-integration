from datetime import datetime
import pytz

# Input ISO 8601 timestamp in UTC
utc_time_str = "2025-01-07T02:42:40.710Z"

# Parse the string to a datetime object
utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")

# Define the UTC and CST timezones
utc_zone = pytz.utc
cst_zone = pytz.timezone("US/Central")

# Assign the UTC timezone to the datetime object
utc_time = utc_zone.localize(utc_time)

# Convert the datetime to CST
cst_time = utc_time.astimezone(cst_zone)

# Print the converted time
print(cst_time)
