"""
Backend App
"""

import sys
import os
import uuid
import base64
import hmac
import hashlib
import json
import asyncio
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from multi_agents.agents import ChiefEditorAgent


# Secret key for HMAC (use a strong key and keep it safe)
SECRET_KEY = b"supersecretkey"

app = Flask(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Run with LangSmith if API key is set
if os.environ.get("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

load_dotenv()


def start_background_task(json_data):
    """
    Runs thread to make sure ai task is not blocking api
    """
    # Launch run_task in a separate thread
    thread = threading.Thread(target=lambda: asyncio.run(run_task(json_data)))
    thread.start()


async def run_task(valid_json_task):
    """
    Actual task being run in the thread
    """
    chief_editor = ChiefEditorAgent(valid_json_task)
    research_report = await chief_editor.run_research_task(task_id=uuid.uuid4())
    return research_report


@app.route("/research", methods=["POST"])
async def research():
    """
    Research endpoint accepts any json, so please make sure json FIELDS are validated somehow lol, align to the project
    """
    try:
        # Get the encoded data from the request
        encoded_data = request.json.get("data")
        signature = request.json.get("signature")  # Optional for tamper-proofing
        print(encoded_data, signature)

        if not encoded_data:
            return jsonify({"error": "No data provided"}), 400

        # Decode the Base64 payload
        decoded_data = base64.urlsafe_b64decode(encoded_data).decode("utf-8")

        # Optional: Validate the signature
        if signature:
            expected_signature = hmac.new(
                SECRET_KEY, encoded_data.encode("utf-8"), hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected_signature):
                return jsonify({"error": "Invalid signature"}), 403

        # Parse the JSON payload
        json_data = json.loads(decoded_data)

        start_background_task(json_data)

        return jsonify(
            {"message": "JSON received successfully", "received_data": json_data}
        )

    except (ValueError, json.JSONDecodeError, base64.binascii.Error) as e:
        return jsonify({"error": "Invalid data format", "details": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
