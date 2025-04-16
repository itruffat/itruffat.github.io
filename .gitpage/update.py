import requests
import base64
import os
import yaml

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_USERNAME")
REPO = os.getenv("GITHUB_REPO").split("/")[1]

if not GITHUB_TOKEN or not USERNAME:
    raise ValueError("""
    Missing information for request in environment variable.
    Please set it up in project configuration.
         Settings > Secrets and Variables.
    Username is a varialbe, Token is a secret.
    """)

HEADERS = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def fetch_repos():
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/user/repos?per_page=100&page={page}"
        res = requests.get(url,headers=HEADERS)
        data = res.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_file_content(owner, repo, file_path):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        content = res.json().get("content", "")
        return base64.b64decode(content).decode('utf-8')
    elif res.status_code == 404:
        return None  # File does not exist
    else:
        raise Exception(f"Error checking {repo}: {res.status_code} {res.text}")


    print(output_content)


def get_existing_sha(owner, repo, file_path):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json().get("sha")
    elif res.status_code == 404:
        return None
    else:
        raise Exception(f"Error checking file: {res.status_code} {res.text}")


def create_or_update_file(owner, repo, file_path, new_content):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    encoded_content = base64.b64encode(new_content.encode()).decode()

    payload = {
        "message": f"Automatically patched {file_path} via gitpages-update",
        "content": encoded_content,
        "branch": "main",  
    }

    sha = get_existing_sha(owner, repo, file_path)
    if sha:
        payload["sha"] = sha  

    res = requests.put(url, headers=HEADERS, json=payload)
    if res.status_code in (200, 201):
        print(f"File '{FILE_PATH}' committed successfully!")
    else:
        raise Exception(f" Failed to commit: {res.status_code}\n{res.text}")



def main():
    repos = fetch_repos()
    owned = [r for r in repos if r["owner"]["login"].lower() == USERNAME.lower()]
    entries = {}
    categories = []


    for repo in owned:
        gitpage_content = get_file_content(USERNAME, repo["name"], ".gitpage/entry.yml")
        if gitpage_content:
            print(f"Found repo: {repo['full_name']} (updated: {repo['updated_at']})")
            try:
                entries[repo["name"]] = yaml.safe_load(gitpage_content)
                entries[repo["name"]]["owner"] = repo["owner"]["login"]
            except yaml.YAMLError as exc:
                print(f"Repo {repo['name']} failed to Parse")
            else:
                if 'skip' in entries[repo["name"]] and entries[repo["name"]]["skip"]:
                    print(f"Repo {repo['name']} skipped by config request")
                    del entries[repo["name"]]
        else:
            print(f"Repo {repo['name']} skipped")

    frozen_content = list(entries.items())

    for name, content in frozen_content:
        if not "category" in content:
            print(f"Repo {name} skipped due to bad config")
            del entries[name]
            continue
        categories.append(content["category"])

    ord_categories = sorted(categories)
    ord_entries = sorted(entries.keys())
    output_content = []

    for category in ord_categories:
        output_content.append(f"> {category.upper()}")
        for entry in ord_entries:
            if entries[entry]["category"] == category:
                link = f"https://github.com/{entries[entry]['owner']}/{entry}"
                output_content.append(f"  * [{link}]({entries[entry]['name']}):  {entries[entry]['description']}")

    summary_path = "repositories_summary.md"

    old_summary = ""
    if os.path.exists(summary_path):
        with open(summary_path, "r") as summary_read:
            old_summary = summary_read.read()

    new_summary = '\n'.join(output_content)

    if old_summary != new_summary:
        create_or_update_file(USERNAME,REPO, summary_path, new_summary)






if __name__ == "__main__":
    print("started")
    print("====")
    main()
    print("====")
    print("ended")
