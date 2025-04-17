import requests
import base64
import os
import yaml

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_USERNAME")
REPO = os.getenv("GITHUB_REPO").split("/")[1]

if not GITHUB_TOKEN or not USERNAME or not REPO:
    raise ValueError("""
    Missing information for request in environment variable.
    Please set it up in project configuration.
         Settings > Secrets and Variables.
    Username is a varialbe, Token is a secret.
    """)

class GithubConnector:

    HEADERS = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


    def fetch_repos(self):
        repos = []
        page = 1
        while True:
            url = f"https://api.github.com/user/repos?per_page=100&page={page}"
            res = requests.get(url,headers=GithubConnector.HEADERS)
            data = res.json()
            if not data:
                break
            repos.extend(data)
            page += 1
        return repos

    def get_file_content(self,owner, repo, file_path):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        res = requests.get(url, headers=GithubConnector.HEADERS)
        content = ""
        if res.status_code == 200:
            content = res.json().get("content", "")
            return base64.b64decode(content).decode('utf-8')
        elif res.status_code == 404:
            return None  
        else:
            raise Exception(f"Error checking {repo}: {res.status_code} {res.text}")



    def get_existing_sha(self,owner, repo, file_path):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        res = requests.get(url, headers=GithubConnector.HEADERS)
        if res.status_code == 200:
            return res.json().get("sha")
        elif res.status_code == 404:
            return None
        else:
            raise Exception(f"Error checking file: {res.status_code} {res.text}")


    def create_or_update_file(self,owner, repo, file_path, new_content):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        encoded_content = base64.b64encode(new_content.encode()).decode()

        payload = {
            "message": f"Automatically patched {file_path} via gitpages-update",
            "content": encoded_content,
            "branch": "main",  
        }

        sha = self.get_existing_sha(owner, repo, file_path)
        if sha:
            payload["sha"] = sha  

        res = requests.put(url, headers=GithubConnector.HEADERS, json=payload)
        if res.status_code in (200, 201):
            print(f"File '{file_path}' committed successfully!")
        else:
            raise Exception(f" Failed to commit: {res.status_code}\n{res.text}")


def produce_summary(categories, entries, summary_path):
    output_content = []
    ord_entries = sorted(entries.keys())
    ord_categories = sorted(categories)

    for category in ord_categories:
        output_content.append(f"> {category.upper()}")
        output_content.append(" ")
        for entry in ord_entries:
            if entries[entry]["category"] == category:
                link = f"https://github.com/{entries[entry]['owner']}/{entry}"
                description = entries[entry]['description']
                description += "\n" if description[-1] != "\n" else ""
                output_content.append(f"  * [{entries[entry]['name']}]({link}):  {description}")
                output_content.append(" ")
                
    old_summary = ""
    if os.path.exists(summary_path):
        with open(summary_path, "r") as summary_read:
            old_summary = summary_read.read()

    new_info = '\n'.join(output_content)

    template_summary = "[REPOS-LIST]"
    if os.path.exists(f"{summary_path}.template"):
        with open(f"{summary_path}.template", "r") as template_read:
            template_summary = template_read.read()

    new_summary = template_summary.replace("[REPOS-LIST]", new_info)

    return new_summary if old_summary != new_summary else None


def run(connector, summary_path):
    repos = connector.fetch_repos()
    owned = [r for r in repos if r["owner"]["login"].lower() == USERNAME.lower()]
    entries = {}
    categories = []


    for repo in owned:
        gitpage_content = connector.get_file_content(USERNAME, repo["name"], ".gitpage/entry.yml")
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
        if content["category"] not in categories:
            categories.append(content["category"])

    summary = produce_summary(categories, entries, summary_path)
    if summary:
        connector.create_or_update_file(USERNAME,REPO, summary_path, summary)



if __name__ == "__main__":
    print("started")
    print("====")
    connector = GithubConnector() 
    run(connector, "README.md")
    print("====")
    print("ended")
