import json

import requests


def send(user_name, message):
    webhook_url = "https://hooks.slack.com/services/***"
    payload = {"username": user_name, "text": message}
    requests.post(
        webhook_url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
