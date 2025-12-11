import json
import re
from typing import Dict
from exponent_server_sdk import PushClient, PushMessage, PushServerError
from requests.exceptions import RequestException

def clean_analysis_result_str(analysis_result: Dict[str, str]) -> Dict:
    """
    Convert a markdown-wrapped, newline-escaped JSON string into a valid Python dictionary.

    Parameters:
    - analysis_result: dict with 'result' key containing markdown-style wrapped JSON string.

    Returns:
    - Parsed JSON as a Python dict.
    """
    raw = analysis_result.get("result", "")

    # Remove ```json and ``` if present
    cleaned = re.sub(r"```json|```", "", raw).strip()

    # Convert escaped newlines and escaped quotes
    try:
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse analysis result: {e}")
    

# Send push notifications
def send_push_notification(expo_token: str, title: str, message: str):
    try:
        response = PushClient().publish(
            PushMessage(
                to=expo_token,
                title=title,
                body=message,
                sound='default'
            )
        )
        print("Push sent:", response)
    except (PushServerError, RequestException) as e:
        print("Error sending push notification:", e)