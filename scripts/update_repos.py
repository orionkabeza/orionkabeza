#!/usr/bin/env python3
"""Rebuild the featured-repos section of the profile README.

Fetches all public, non-fork repos for the user via the GitHub API and
rewrites the block between <!-- REPOS:START --> and <!-- REPOS:END -->.
Everything outside the markers is left untouched.
"""

import json
import os
import sys
import urllib.request

USERNAME = "orionkabeza"
README = "README.md"
START = "<!-- REPOS:START -->"
END = "<!-- REPOS:END -->"
EXCLUDE = {USERNAME}  # skip the profile repo itself


def fetch_repos():
    repos, page = [], 1
    token = os.environ.get("GITHUB_TOKEN", "")
    while True:
        req = urllib.request.Request(
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?per_page=100&page={page}&sort=pushed"
        )
        req.add_header("Accept", "application/vnd.github+json")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req) as r:
            batch = json.load(r)
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return [
        r for r in repos
        if not r["fork"] and not r["private"] and not r["archived"]
        and r["name"] not in EXCLUDE
    ]


def build_table(repos):
    lines = [
        "| Repository | Description | Language | ⭐ |",
        "|---|---|---|---|",
    ]
    for r in repos:
        desc = (r["description"] or "—").replace("|", "\\|")
        lang = r["language"] or "—"
        lines.append(
            f"| [**{r['name']}**]({r['html_url']}) | {desc} | {lang} | {r['stargazers_count']} |"
        )
    return "\n".join(lines)


def main():
    with open(README, encoding="utf-8") as f:
        content = f.read()

    if START not in content or END not in content:
        sys.exit(f"Markers {START} / {END} not found in {README}")

    repos = fetch_repos()
    table = build_table(repos)
    head = content.split(START)[0]
    tail = content.split(END)[1]
    new = f"{head}{START}\n{table}\n{END}{tail}"

    if new != content:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new)
        print(f"README updated with {len(repos)} repos.")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
