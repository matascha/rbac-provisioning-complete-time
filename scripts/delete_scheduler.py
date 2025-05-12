import requests, json, datetime
from base64 import b64decode, b64encode

# CONFIG
REPO = "matascha/rbac-provisioning-complete"
FILE_PATH = "scripts/pending_delete.json"
GITHUB_TOKEN = "ghp_xxx"
AWX_URL = "https://awx.domain.com/api/v2/job_templates/123/launch/"
AWX_TOKEN = "awx_xxx"
TIME_WINDOW_MIN = 5

def fetch_schedule():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    res = requests.get(url, headers=headers)
    data = res.json()
    content = json.loads(b64decode(data["content"]))
    return content, data["sha"]

def push_schedule(content, sha):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    payload = {
        "message": "🧹 Cleaned executed deletions",
        "content": b64encode(json.dumps(content, indent=2).encode()).decode(),
        "sha": sha,
        "committer": {
            "name": "Scheduler Bot",
            "email": "bot@yourdomain.com"
        }
    }
    res = requests.put(url, headers=headers, json=payload)
    print("✅ GitHub updated:", res.status_code)

def process_deletions(schedule):
    now = datetime.datetime.now()
    executed = []
    for time_str, users in schedule.items():
        scheduled = datetime.datetime.fromisoformat(time_str)
        diff = (scheduled - now).total_seconds() / 60
        if abs(diff) <= TIME_WINDOW_MIN:
            for user in users:
                print(f"🚀 Deleting {user}")
                headers = {
                    "Authorization": f"Bearer {AWX_TOKEN}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "extra_vars": {
                        "username": user,
                        "delete_time": time_str
                    }
                }
                res = requests.post(AWX_URL, json=payload, headers=headers)
                print(f"AWX response: {res.status_code}")
            executed.append(time_str)
    return executed

if __name__ == "__main__":
    schedule, sha = fetch_schedule()
    done = process_deletions(schedule)
    if done:
        for key in done:
            del schedule[key]
        push_schedule(schedule, sha)
