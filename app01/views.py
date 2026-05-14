import subprocess
import os

from django.shortcuts import render

def home(request):
    """主页"""
    version = "1.0"
    commit_msg = ""
    commit_date = ""
    try:
        repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tag = subprocess.run(
            ["git", "tag", "--sort=-version:refname"],
            capture_output=True, text=True, cwd=repo_dir, timeout=5
        )
        tags = [t.strip() for t in tag.stdout.split() if t.strip()]
        if tags:
            version = tags[0].lstrip("v")
        log = subprocess.run(
            ["git", "log", "-1", f"{tags[0] if tags else HEAD}", "--format=%s|%ci"],
            capture_output=True, text=True, cwd=repo_dir, timeout=5
        )
        parts = log.stdout.strip().split("|")
        if len(parts) >= 2:
            commit_msg = parts[0]
            commit_date = parts[1][:10]
    except Exception:
        pass
    return render(request, "home.html", {
        "version": version,
        "commit_msg": commit_msg,
        "commit_date": commit_date,
    })
