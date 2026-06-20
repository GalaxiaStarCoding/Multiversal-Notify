"""
server/fcm.py

Simple FCM legacy HTTP v1 sender using server key. This is an example and
uses the legacy FCM API (https://fcm.googleapis.com/fcm/send) for simplicity.
For production you should use the HTTP v1 API with OAuth2 tokens or a
Google service account and the Firebase Admin SDK.
"""

import os
import json
import requests
from typing import List, Tuple

FCM_LEGACY_URL = 'https://fcm.googleapis.com/fcm/send'


def send_to_fcm(server_key: str, tokens: List[str], title: str, body: str, data: dict = None) -> Tuple[bool, dict]:
    headers = {
        'Authorization': 'key=%s' % server_key,
        'Content-Type': 'application/json'
    }

    payload = {
        'registration_ids': tokens,
        'priority': 'high',
        'notification': {
            'title': title,
            'body': body,
        },
        'data': data or {}
    }

    try:
        r = requests.post(FCM_LEGACY_URL, headers=headers, json=payload, timeout=8)
        r.raise_for_status()
        return True, r.json()
    except Exception as e:
        return False, {'error': str(e)}
