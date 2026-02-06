"""
Example clients for the simple REST API (GET / POST).
Use these from Python or as reference for curl/fetch.
"""

import json
import urllib.request
import urllib.error

BASE = "http://localhost:8002"  # default port for api_server.py


def get_crew():
    """GET /api/crew — health/description."""
    req = urllib.request.Request(
        f"{BASE}/api/crew",
        method="GET",
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def post_crew(message: str, language: str = None, campaign_context: str = None):
    """POST /api/crew — run crew."""
    body = {"message": message}
    if language:
        body["language"] = language
    if campaign_context:
        body["campaign_context"] = campaign_context

    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}/api/crew",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=320) as resp:
        return json.loads(resp.read().decode())


if __name__ == "__main__":
    print("GET /api/crew:", get_crew())
    print("POST /api/crew (short message):", post_crew("Create a one-sentence content idea."))
