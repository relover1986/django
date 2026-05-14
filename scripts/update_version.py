#!/usr/bin/env python3
import os, re, subprocess, sys

BASE = '/root/django'
os.chdir(BASE)

tag = subprocess.run(
    ['git', 'tag', '--sort=-version:refname'],
    capture_output=True, text=True, timeout=5
)
tags = [t.strip() for t in tag.stdout.split() if t.strip()]
if not tags:
    print('no tags'); sys.exit(1)
latest_tag = tags[0]
version = latest_tag.lstrip('v')

log = subprocess.run(
    ['git', 'log', '-1', latest_tag, '--format=%s|%ci'],
    capture_output=True, text=True, timeout=5
)
parts = log.stdout.strip().split('|')
commit_msg = parts[0] if len(parts) >= 1 else ''
commit_date = parts[1][:10] if len(parts) >= 2 else ''

print(f'{latest_tag} -> v{version} | {commit_date} | {commit_msg}')

html_path = 'app01/templates/home.html'
with open(html_path, 'r') as f:
    html = f.read()

pat = r'(<div class="text-center mt-5 pt-5">\s*<p class="lead" style="font-size:1\.5rem;">\s*<span class="badge bg-primary fs-5 me-2">)v[^<]+(</span>\s*<span class="text-muted">)[^<]+(</span>\s*</p>\s*<p class="text-muted" style="font-size:1\.1rem;">)[^<]+(</p>\s*</div>)'
rep = rf'\g<1>v{version}\g<2>{commit_date}\g<3>{commit_msg}\g<4>'

if re.search(pat, html):
    html = re.sub(pat, rep, html)
    with open(html_path, 'w') as f:
        f.write(html)
    print('home.html updated')
else:
    print('version block not found'); sys.exit(1)

subprocess.run(['git', 'add', '-A'], check=True, timeout=10)
subprocess.run(['git', 'commit', '-m', f'首页版本号 v{version}'], check=True, timeout=10)
subprocess.run(['git', 'push'], check=True, timeout=30)
print('git pushed')

subprocess.run(['pm2', 'restart', '0'], check=True, timeout=10)
print('pm2 restarted')
print('DONE')
