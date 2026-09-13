"""
Codeforces Solutions Sync
Fetches accepted submissions from Codeforces and archives them.
"""

import os
import sys
import requests
import json
import time
from datetime import datetime, timezone


# ─── Configuration (loaded from environment / GitHub Secrets) ───
GIT_NAME = os.environ.get("GIT_NAME", "jetashjethi-ui")
GIT_EMAIL = os.environ.get("GIT_EMAIL", "jetashjethi@gmail.com")
CF_HANDLE = os.environ.get("CF_HANDLE", "Jitesh_jethi")


# ─── Helper: git commit with a specific date ───
def git_commit(filepath, message, date_str):
    """Stage a file and commit."""
    os.system(f'git add "{filepath}"')
    env_prefix = f'GIT_AUTHOR_DATE="{date_str}" GIT_COMMITTER_DATE="{date_str}"'
    os.system(
        f'{env_prefix} git commit -m "{message}" '
        f'--author="{GIT_NAME} <{GIT_EMAIL}>"'
    )


# ─── Helper: load already-synced submission IDs ───
SYNCED_FILE = ".synced_ids.json"

def load_synced():
    if os.path.exists(SYNCED_FILE):
        with open(SYNCED_FILE, "r") as f:
            return json.load(f)
    return {"codeforces": []}

def save_synced(data):
    with open(SYNCED_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CODEFORCES SYNC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def sync_codeforces(synced):
    if not CF_HANDLE:
        print("CF_HANDLE not set — skipping.")
        return

    print(f"Fetching Codeforces submissions for: {CF_HANDLE} ...")
    url = f"https://codeforces.com/api/user.status?handle={CF_HANDLE}&from=1&count=100"

    try:
        res = requests.get(url, timeout=30)
        data = res.json()
    except Exception as e:
        print(f"Codeforces API error: {e}")
        return

    if data.get("status") != "OK":
        print(f"Codeforces API error: {data.get('comment', 'Unknown error')}")
        return

    ext_map = {
        "c++": "cpp", "gnu c++": "cpp", "g++": "cpp",
        "python": "py", "pypy": "py",
        "java": "java", "kotlin": "kt",
        "rust": "rs", "javascript": "js",
        "c#": "cs", "go": "go",
    }

    new_count = 0
    for sub in reversed(data["result"]):  # oldest first
        if sub.get("verdict") != "OK":
            continue

        sub_id = str(sub["id"])
        if sub_id in synced.get("codeforces", []):
            continue

        prob = sub["problem"]
        contest_id = prob.get("contestId", "0")
        index = prob.get("index", "A")
        name = prob.get("name", "Problem").replace(" ", "_").replace("/", "-")
        lang_raw = sub.get("programmingLanguage", "").lower()
        timestamp = sub["creationTimeSeconds"]
        date_str = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

        ext = "txt"
        for key, val in ext_map.items():
            if key in lang_raw:
                ext = val
                break

        folder = f"Codeforces/{contest_id}"
        os.makedirs(folder, exist_ok=True)
        filepath = f"{folder}/{index}_{name}.{ext}"

        if os.path.exists(filepath):
            synced.setdefault("codeforces", []).append(sub_id)
            continue

        content = (
            f"// Problem  : {contest_id}{index} - {prob.get('name')}\n"
            f"// Contest  : https://codeforces.com/contest/{contest_id}/problem/{index}\n"
            f"// Language : {sub.get('programmingLanguage')}\n"
            f"// Verdict  : Accepted\n"
            f"// Date     : {date_str}\n\n"
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        commit_msg = f"Add CF {contest_id}{index}: {prob.get('name')}"
        git_commit(filepath, commit_msg, date_str)

        synced.setdefault("codeforces", []).append(sub_id)
        new_count += 1

    print(f"Codeforces: {new_count} new solution(s) committed.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    os.system(f'git config user.name "{GIT_NAME}"')
    os.system(f'git config user.email "{GIT_EMAIL}"')

    synced = load_synced()
    sync_codeforces(synced)

    save_synced(synced)
    os.system(f'git add "{SYNCED_FILE}"')
    os.system('git commit -m "Update sync tracker" --allow-empty || true')

    print("Sync complete!")
