import os
import requests
API_URL = "https://api.together.xyz/api/inference"
headers = {"Authorization": os.environ.get(
    "TOGETHER_API_KEY", "together-api-key")}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()