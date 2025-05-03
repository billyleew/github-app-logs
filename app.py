from flask import flask, request, jsonify
import requests
import os
from github_auth import get_installation_token
from dotenv import load_dotenv
import gzip

load_dotenv()

app = flask(__name__)
LOG_RECEIVER_URL = os.getenv("LOG_RECEIVER_URL")

@app.route("/webhook", methods=["POST"])
def webhook():
    event_type = request.headers.get("X-GitHub-Event")
    payload = request.json

    if event_type in ["workflow_job", "workflow_run"] and payload.get("action") == "completed":
        installation_id = payload["installation"]["id"]
        repo = payload["repository"]["full_name"]
        run_id = payload.get("workflow_run", {}).get("id")

        if run_id:
            try:
                token = get_installation_token(installation_id)
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github+json"
                }

                # Download logs
                logs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
                resp = requests.get(logs_url, headers=headers)
                if resp.status_code == 200:
                    # Decompress log
                    log_data = gzip.decompress(resp.content).decode("utf-8")

                    # Send to log receiver
                    post_resp = requests.post(LOG_RECEIVER_URL, json={
                        "repo": repo,
                        "run_id": run_id,
                        "log": log_data
                    })

                    return jsonify({"status": "log sent", "log_api_response": post_resp.status_code}), 200
                else:
                    return jsonify({"error": "Failed to fetch logs", "github_response": resp.status_code}), 500
            except Exception as e:
                return jsonify({"error": str(e)}), 500
                
        return jsonify({"status": "ignored"}), 200