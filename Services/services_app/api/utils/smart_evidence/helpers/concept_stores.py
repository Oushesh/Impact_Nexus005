import os
from typing import Dict, List

import requests
from smart_evidence.helpers.assessment_service_auth import get_bearer_token


def get_concepts(params) -> List[Dict]:
    """Raises :class:`HTTPError`, if one occurred."""
    bearer_token = get_bearer_token()

    response = requests.get(
        f"{os.environ['ASSESSMENT_SERVICE_ENDPOINT']}/concepts/company",
        params=params,
        headers={"authorization": f"Bearer {bearer_token}"},
        timeout=300,
    )
    if response.status_code == 200:
        return response.json()

    response.raise_for_status()
    return []
