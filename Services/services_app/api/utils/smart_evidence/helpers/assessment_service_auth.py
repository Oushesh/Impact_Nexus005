import os
import requests


def get_bearer_token():
    payload = {
        "client_id": os.environ["AUTH0_CLIENT_ID"],
        "client_secret": os.environ["AUTH0_CLIENT_SECRET"],
        "audience": os.environ["AUTH0_AUDIENCE"],
        "grant_type": os.environ["AUTH0_GRANT_TYPE"],
    }
    headers = {"content-type": "application/json"}
    response = requests.post(
        "https://impactnexus.eu.auth0.com/oauth/token",
        json=payload,
        headers=headers,
        timeout=300,
    )
    return response.json()["access_token"]