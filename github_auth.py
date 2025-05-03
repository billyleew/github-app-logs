import jwt
import time
import requests
from dotenv import load_dotenv
import os

load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

def generate_jwt():
    with open(PRIVATE_KEY_PATH, "r") as pem_file:
        private_key = pem_file.read()
    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": APP_ID
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

def get_installation_token(installation_id):
    jwt_token = generate_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(url, headers=headers)
    return response.json()["token"]