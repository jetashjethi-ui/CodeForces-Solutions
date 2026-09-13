import os
import requests
import json
from datetime import datetime, timezone

GIT_NAME = os.environ.get("GIT_NAME", "jetashjethi-ui")
GIT_EMAIL = os.environ.get("GIT_EMAIL", "jetashjethi@gmail.com")
CF_HANDLE = os.environ.get("CF_HANDLE", "Jitesh_jethi")

SYNCED_FILE = ".synced_ids.json"

def load_synced():
    if os.path.exists(SYNCED_FILE):
        with open(SYNCED_FILE, "r") as f:
            return json.load(f)
    return []

def save_synced(data):
    with open(SYNCED_FILE, "w") as f:
        json.dump(data, f)

def get_extension(lang):
    lang = lang.lower()
    if "c++" in lang or "g++" in lang:
        return "cpp"
    if "python" in lang or "pypy" in lang:
        return "py"
    if "java" in lang:
        return "java"
    if "kotlin" in lang:
        return "kt"
    if "rust" in lang:
        return "rs"
    if "javascript" in lang:
        return "js"
    if "go" in lang:
        return "go"
    return "txt"

def main():
    os.system(f'git config user.name "{GIT_NAME}"')
    os.system(f'git config user.email "{GIT_EMAIL}"')

    synced = load_synced()

    url = f"https://codeforces.com/api/user.status?handle={CF_HANDLE}&from=1&count=100"
    res = requests.get(url, timeout=30).json()

    if res.get("status") != "OK":
        print("failed to fetch:", res.get("comment"))
        return

    count = 0
    for sub in reversed(res["result"]):
        if sub.get("verdict") != "OK":
            continue

        sub_id = str(sub["id"])
        if sub_id in synced:
            continue

        prob = sub["problem"]
        cid = prob.get("contestId", "0")
        idx = prob.get("index", "A")
        name = prob.get("name", "problem").replace(" ", "_").replace("/", "-")
        lang = sub.get("programmingLanguage", "")
        ts = sub["creationTimeSeconds"]
        date = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        ext = get_extension(lang)

        folder = f"Codeforces/{cid}"
        os.makedirs(folder, exist_ok=True)
        path = f"{folder}/{idx}_{name}.{ext}"

        if os.path.exists(path):
            synced.append(sub_id)
            continue

        with open(path, "w") as f:
            f.write(f"// {cid}{idx} - {prob.get('name')}\n")
            f.write(f"// https://codeforces.com/contest/{cid}/problem/{idx}\n\n")

        os.system(f'git add "{path}"')
        os.system(
            f'GIT_AUTHOR_DATE="{date}" GIT_COMMITTER_DATE="{date}" '
            f'git commit -m "solve {cid}{idx} {prob.get("name")}"'
        )

        synced.append(sub_id)
        count += 1

    save_synced(synced)
    os.system(f'git add {SYNCED_FILE}')
    os.system('git commit -m "update tracker" --allow-empty || true')
    print(f"done, {count} new")

if __name__ == "__main__":
    main()
