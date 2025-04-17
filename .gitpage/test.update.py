import os
from update import run


class MockGithubConnector:

    def __init__(self, initialization):
        self.repos = initialization["repos"]
        self.content = initialization["content"]
        self.expectations = initialization["expectations"]
        self.seen = []

    def fetch_repos(self):
        return self.repos

    def get_file_content(self, _ , repo, _ ):
        return self.content[repo] if repo in self.content.keys() else None 

    def create_or_update_file(self, _ , repo, _, new_content, _):
        if not self.expectations or repo not in self.expectations.keys():
            print(repo)
            print(new_content)
        else:
            assert( self.expectations[repo]  == new_content)
            self.seen.append(repo)

    def assert_all_seen(self):
        if self.expectations:
            assert(set(self.seen) == set(self.expectations.keys()))


def folder_to_init(folder):
    init = {
        "expectations": None,
        "repos": {},
        "content": {}
    }

    repo_pattern = re.compile(r"^(?P<name>.+)\.repo\.yaml$")
    content_pattern = re.compile(r"^(?P<name>.+)\.content\.yaml$")

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            if file == "expectations.txt":
                with open(file_path, 'r') as f:
                    init["expectations"] = f.read()

            elif repo_match := repo_pattern.match(file):
                name = repo_match.group("name")
                with open(file_path, 'r') as f:
                    init["repos"][name] = yaml.safe_load(f)

            elif content_match := content_pattern.match(file):
                name = content_match.group("name")
                with open(file_path, 'r') as f:
                    content_data = yaml.safe_load(f)

                if name in init["repos"]:
                    init["content"][name] = content_data

    return init


