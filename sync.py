"""
Competitive Programming Auto-Sync to GitHub
Fetches accepted submissions from LeetCode & Codeforces,
commits each with its original timestamp so your GitHub heatmap turns GREEN.
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
LEETCODE_SESSION = os.environ.get("LEETCODE_SESSION", "")
LEETCODE_CSRFTOKEN = os.environ.get("LEETCODE_CSRFTOKEN", "")


# ─── Helper: git commit with a specific date ───
def git_commit(filepath, message, date_str):
    """Stage a file and commit with a historical date."""
    os.system(f'git add "{filepath}"')
    # Set both author and committer date so GitHub credits the correct day
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
    return {"leetcode": [], "codeforces": []}

def save_synced(data):
    with open(SYNCED_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  1. CODEFORCES SYNC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def sync_codeforces(synced):
    if not CF_HANDLE:
        print("⚠  CF_HANDLE not set — skipping Codeforces.")
        return

    print(f"🔄 Fetching Codeforces submissions for: {CF_HANDLE} ...")
    url = f"https://codeforces.com/api/user.status?handle={CF_HANDLE}&from=1&count=100"

    try:
        res = requests.get(url, timeout=30)
        data = res.json()
    except Exception as e:
        print(f"❌ Codeforces API error: {e}")
        return

    if data.get("status") != "OK":
        print(f"❌ Codeforces API error: {data.get('comment', 'Unknown error')}")
        return

    ext_map = {
        "c++": "cpp", "gnu c++": "cpp", "g++": "cpp",
        "python": "py", "pypy": "py",
        "java": "java", "kotlin": "kt",
        "rust": "rs", "javascript": "js",
        "c#": "cs", "go": "go",
    }

    new_count = 0
    for sub in reversed(data["result"]):  # oldest first → chronological commits
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

        # Write solution metadata (Codeforces API doesn't expose source code publicly)
        content = (
            f"// ============================================\n"
            f"// Problem  : {contest_id}{index} — {prob.get('name')}\n"
            f"// Contest  : https://codeforces.com/contest/{contest_id}/problem/{index}\n"
            f"// Language : {sub.get('programmingLanguage')}\n"
            f"// Verdict  : Accepted\n"
            f"// Date     : {date_str}\n"
            f"// Sub ID   : {sub_id}\n"
            f"// ============================================\n\n"
            f"// Paste your solution here, or use a browser extension\n"
            f"// to auto-capture source code.\n"
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        commit_msg = f"✅ CF {contest_id}{index}: {prob.get('name')}"
        git_commit(filepath, commit_msg, date_str)

        synced.setdefault("codeforces", []).append(sub_id)
        new_count += 1

    print(f"✅ Codeforces: {new_count} new solution(s) committed.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  2. LEETCODE SYNC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fetch_leetcode_submissions(offset=0, limit=20):
    """Fetch recent submissions from LeetCode's API."""
    url = f"https://leetcode.com/api/submissions/?offset={offset}&limit={limit}"
    headers = {
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={LEETCODE_CSRFTOKEN}",
        "Referer": "https://leetcode.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-CSRFToken": LEETCODE_CSRFTOKEN,
    }
    try:
        res = requests.get(url, headers=headers, timeout=30)
        if res.status_code != 200:
            print(f"❌ LeetCode API returned status {res.status_code}")
            return []
        return res.json().get("submissions_dump", [])
    except Exception as e:
        print(f"❌ LeetCode API error: {e}")
        return []


def sync_leetcode(synced):
    if not LEETCODE_SESSION:
        print("⚠  LEETCODE_SESSION not set — skipping LeetCode.")
        return

    print("🔄 Fetching LeetCode submissions ...")

    ext_map = {
        "python3": "py", "python": "py",
        "cpp": "cpp", "c++": "cpp", "c": "c",
        "java": "java", "kotlin": "kt",
        "javascript": "js", "typescript": "ts",
        "rust": "rs", "go": "go", "swift": "swift",
        "csharp": "cs", "ruby": "rb", "scala": "scala",
        "dart": "dart", "php": "php",
    }

    all_subs = []
    offset = 0
    # Fetch up to 200 recent submissions (10 pages × 20)
    for _ in range(10):
        batch = fetch_leetcode_submissions(offset=offset, limit=20)
        if not batch:
            break
        all_subs.extend(batch)
        offset += 20
        time.sleep(1)  # Be polite to the API

    new_count = 0
    # Process oldest first for chronological commits
    for sub in reversed(all_subs):
        if sub.get("status_display") != "Accepted":
            continue

        sub_id = str(sub.get("id", sub.get("timestamp", "")))
        if sub_id in synced.get("leetcode", []):
            continue

        title = sub["title"].replace(" ", "_").replace("/", "-")
        title_slug = sub.get("title_slug", title.lower())
        timestamp = sub["timestamp"]
        date_str = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        lang = sub.get("lang", "cpp").lower()
        code = sub.get("code", "")
        ext = ext_map.get(lang, "txt")

        folder = "LeetCode"
        os.makedirs(folder, exist_ok=True)
        filepath = f"{folder}/{title}.{ext}"

        if os.path.exists(filepath):
            synced.setdefault("leetcode", []).append(sub_id)
            continue

        # Write the actual solution code
        header = (
            f"# Problem : {sub['title']}\n"
            f"# Link    : https://leetcode.com/problems/{title_slug}/\n"
            f"# Language: {lang}\n"
            f"# Date    : {date_str}\n\n"
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header + code + "\n")

        commit_msg = f"✅ LC: {sub['title']}"
        git_commit(filepath, commit_msg, date_str)

        synced.setdefault("leetcode", []).append(sub_id)
        new_count += 1

    print(f"✅ LeetCode: {new_count} new solution(s) committed.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    # Configure git identity
    os.system(f'git config user.name "{GIT_NAME}"')
    os.system(f'git config user.email "{GIT_EMAIL}"')

    synced = load_synced()

    sync_codeforces(synced)
    sync_leetcode(synced)

    # Save progress so we don't re-commit next run
    # Stage the tracker file too
    save_synced(synced)
    os.system(f'git add "{SYNCED_FILE}"')
    os.system('git commit -m "📝 Update sync tracker" --allow-empty || true')

    print("\n🎉 Sync complete! Push with:  git push origin main")
