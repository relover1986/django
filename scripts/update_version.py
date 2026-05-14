#!/usr/bin/env python3
"""更新首页版本历史：取所有tag按版本排序 -> 写进home.html -> git commit -> git push -> pm2 restart"""
import os, re, subprocess, sys

BASE = '/root/django'
os.chdir(BASE)

# 1. 获取所有 tag 及对应 commit 信息（从旧到新）
result = subprocess.run(
    ['git', 'tag', '--sort=version:refname'],
    capture_output=True, text=True, timeout=5
)
tags = [t.strip() for t in result.stdout.split() if t.strip()]
if not tags:
    print('no tags'); sys.exit(1)

# 反转 → 最新的在上面
tags.reverse()

rows = []
for t in tags:
    log = subprocess.run(
        ['git', 'log', '-1', t, '--format=%s|%ci'],
        capture_output=True, text=True, timeout=5
    )
    parts = log.stdout.strip().split('|')
    msg = parts[0] if len(parts) >= 1 else ''
    date = parts[1][:10] if len(parts) >= 2 else ''
    ver = t.lstrip('v')
    rows.append((ver, date, msg))
    print(f'  {t}  {date}  {msg}')

# 2. 生成版本历史 HTML
lines = []
for ver, date, msg in rows:
    lines.append(f'''    <div class="text-center mt-3">
        <p class="lead" style="font-size:1.3rem;">
            <span class="badge bg-primary fs-6 me-2">v{ver}</span>
            <span class="text-muted">{date}</span>
        </p>
        <p class="text-muted" style="font-size:1.0rem;">{msg}</p>
    </div>''')

new_block = '\n'.join(lines)

# 3. 替换 home.html 中的版本块
html_path = 'app01/templates/home.html'
with open(html_path, 'r') as f:
    html = f.read()

# 找版本块起始标记
start_tag = '<!-- VERSION_HISTORY_START -->'
end_tag = '<!-- VERSION_HISTORY_END -->'

old_pattern = rf'{re.escape(start_tag)}.*?{re.escape(end_tag)}'
new_content = f'{start_tag}\n{new_block}\n    {end_tag}'

if re.search(old_pattern, html, re.DOTALL):
    html = re.sub(old_pattern, new_content, html, flags=re.DOTALL)
else:
    # 第一次运行，在 block content 中插入
    old_block_pattern = r'(<div class="text-center mt-5 pt-5">.*?</div>)'
    replacement = f'{start_tag}\n{new_block}\n    {end_tag}'
    if re.search(old_block_pattern, html, re.DOTALL):
        html = re.sub(old_block_pattern, replacement, html, flags=re.DOTALL)
    else:
        print('version block not found'); sys.exit(1)

with open(html_path, 'w') as f:
    f.write(html)
print('home.html updated')

subprocess.run(['git', 'add', '-A'], check=True, timeout=10)
subprocess.run(['git', 'commit', '-m', '首页版本历史'], check=True, timeout=10)
subprocess.run(['git', 'push'], check=True, timeout=30)
print('git pushed')
subprocess.run(['pm2', 'restart', '0'], check=True, timeout=10)
print('pm2 restarted DONE')
