"""
Fake Frontend
Used to send json to backend app.py
"""

import base64
import hmac
import hashlib
import json
import requests

# Backend URL
url = "http://127.0.0.1:5000/research"

# JSON data to send
data = {
    "query": "Is AI in a hype cycle?",
    "max_sections": 3,
    "publish_formats": {"markdown": True, "pdf": True, "docx": True},
    "include_human_feedback": False,
    "follow_guidelines": False,
    "model": "gpt-4o",
    "guidelines": [
        "The report MUST be written in APA format",
        "Each sub section MUST include supporting sources using hyperlinks. If none exist, erase the sub section or rewrite it to be a part of the previous section",
        "The report MUST be written in spanish",
    ],
    "verbose": True,
}
# Convert JSON to a string and Base64 encode it
json_str = json.dumps(data)
encoded_data = base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")

# Generate a tamper-proof signature
SECRET_KEY = b"supersecretkey"
signature = hmac.new(
    SECRET_KEY, encoded_data.encode("utf-8"), hashlib.sha256
).hexdigest()

# Send the data and signature
payload = {"data": encoded_data, "signature": signature}
response = requests.post(url, json=payload)

# Print the response
print(response)
