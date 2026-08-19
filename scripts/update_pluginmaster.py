#!/usr/bin/env python3
"""Rebuilds pluginmaster.json from plugins.json by reading each plugin's
manifest file and latest GitHub release.

Add a new plugin by adding an entry to plugins.json - nothing else in this
script needs to change.
"""
import json
import os
import sys
import urllib.request
import urllib.error

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
API_ROOT = "https://api.github.com"


def gh_get(url):
    req = urllib.request.Request(url)
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def raw_get_json(repo, branch, path):
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def build_entry(plugin_cfg):
    repo = plugin_cfg["repo"]
    repo_info = gh_get(f"{API_ROOT}/repos/{repo}")
    default_branch = repo_info["default_branch"]

    manifest = raw_get_json(repo, default_branch, plugin_cfg["manifestPath"])

    try:
        release = gh_get(f"{API_ROOT}/repos/{repo}/releases/latest")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"WARNING: {repo} has no releases yet, skipping", file=sys.stderr)
            return None
        raise

    version = release["tag_name"].lstrip("v")
    zip_asset = next(
        (a for a in release.get("assets", []) if a["name"].endswith(".zip")),
        None,
    )
    download_url = (
        zip_asset["browser_download_url"]
        if zip_asset
        else f"https://github.com/{repo}/releases/download/{release['tag_name']}/latest.zip"
    )

    entry = {
        "Author": manifest["Author"],
        "Name": manifest["Name"],
        "Punchline": manifest.get("Punchline", ""),
        "Description": manifest.get("Description", ""),
        "Changelog": release.get("body") or "",
        "IsHide": False,
        "InternalName": manifest["InternalName"],
        "AssemblyVersion": version,
        "IsTestingExclusive": False,
        "RepoUrl": manifest.get("RepoUrl", f"https://github.com/{repo}"),
        "ApplicableVersion": manifest.get("ApplicableVersion", "any"),
        "DalamudApiLevel": manifest["DalamudApiLevel"],
        "LastUpdate": int(
            __import__("datetime")
            .datetime.strptime(release["published_at"], "%Y-%m-%dT%H:%M:%SZ")
            .timestamp()
        ),
        "DownloadLinkInstall": download_url,
        "DownloadLinkUpdate": download_url,
        "DownloadLinkTesting": download_url,
        "IconUrl": f"https://raw.githubusercontent.com/{repo}/{default_branch}/{plugin_cfg['iconPath']}",
    }
    return entry


def main():
    with open("plugins.json", encoding="utf-8") as f:
        plugins = json.load(f)

    entries = []
    for plugin_cfg in plugins:
        entry = build_entry(plugin_cfg)
        if entry is not None:
            entries.append(entry)

    with open("pluginmaster.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(entries)} plugin entries to pluginmaster.json")


if __name__ == "__main__":
    main()
