import requests
import base64
import os
import yaml
import sys

try:
    from .update import GithubConnector, USERNAME, REPO
except: ## Kind of an ugly solution, but github does not allow me to use relative directories outside of packages
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    from update import GithubConnector, USERNAME, REPO

RUN_MIRROR = os.getenv("RUN_MIRROR")


def run(connector):

    with open("README.md", "r") as readme_file:
        gitpage_content = readme_file.read()
    userpage_content = connector.get_file_content(USERNAME, USERNAME, "README.md")

    if gitpage_content != userpage_content:
        connector.create_or_update_file(USERNAME,USERNAME, "README.md", gitpage_content)


if __name__ == "__main__":
    print("started (mirroring)")
    print("====")
    connector = GithubConnector() 
    if RUN_MIRROR:
        run(connector)
    else:
        print("skipped mirroring")
    print("====")
    print("ended (mirroring)")
