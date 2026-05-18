#!/usr/bin/env python3
"""
版本发布工具：自动计算下个版本 → 打 tag → 推送 → 更新首页 → 创建 GitHub Release
用法：
  python3 scripts/update_version.py           # 自动累加小版本
  python3 scripts/update_version.py 2.0       # 手动指定版本
"""
import os, re, subprocess, sys, argparse

BASE = '/root/django'
os.chdir(BASE)

# --- 解析参数 ---
parser = argparse.ArgumentParser()
parser.add_argument('version', nargs='?', help='手动指定版本，如 2.0')
args = parser.parse_args()

# --- 1. 计算版本 ---
result = subprocess.run(['git', 'tag', '--sort=-version:refname'],
                        capture_output=True, text=True, timeout=5)
tags = [t.strip() for t in result.stdout.split() if t.strip()]

if args.version:
    new_ver = args.version
    print(f'手动指定版本: v{new_ver}')
else:
    if tags:
        latest = tags[0].lstrip('v')
        parts = latest.split('.')
        major = int(parts[0])
        minor = int(parts[1]) + 1 if len(parts) > 1 else 1
        new_ver = f'{major}.{minor}'
    else:
        new_ver = '1.0'
    print(f'自动累加版本: {tags[0] if tags else "(无)"} → v{new_ver}')

new_tag = f'v{new_ver}'

# --- 2. 获取当前最新 commit 信息 ---
log = subprocess.run(['git', 'log', '-1', 'HEAD', '--format=%s|%ci'],
                     capture_output=True, text=True, timeout=5)
parts = log.stdout.strip().split('|')
head_msg = parts[0] if len(parts) >= 1 else ''
head_date = parts[1][:10] if len(parts) >= 2 else ''

# --- 3. 创建并推送 tag ---
subprocess.run(['git', 'tag', '-a', new_tag, '-m', head_msg], check=True, timeout=10)
subprocess.run(['git', 'push', 'origin', new_tag], check=True, timeout=30)
print(f'✅ tag {new_tag} 已创建并推送')

# --- 4. 获取所有 tag 信息（用于首页 + Release notes）---
result2 = subprocess.run(['git', 'tag', '--sort=version:refname'],
                         capture_output=True, text=True, timeout=5)
all_tags = [t.strip() for t in result2.stdout.split() if t.strip()]
all_tags.reverse()

rows = []
for t in all_tags:
    l = subprocess.run(['git', 'log', '-1', t, '--format=%s|%ci'],
                       capture_output=True, text=True, timeout=5)
    p = l.stdout.strip().split('|')
    rows.append((t.lstrip('v'), p[1][:10] if len(p) >= 2 else '', p[0] if len(p) >= 1 else ''))
    print(f'  {t}  {p[1][:10] if len(p) >= 2 else ""}  {p[0] if len(p) >= 1 else ""}')

# --- 5. 更新 home.html ---
html_lines = []
for ver, date, msg in rows:
    html_lines.append(f'''    <div class="text-center mt-3">
        <p class="lead" style="font-size:1.3rem;">
            <span class="badge bg-primary fs-6 me-2">v{ver}</span>
            <span class="text-muted">{date}</span>
        </p>
        <p class="text-muted" style="font-size:1.0rem;">{msg}</p>
    </div>''')

new_block = '\n'.join(html_lines)
html_path = 'app01/templates/home.html'
with open(html_path, 'r') as f:
    html = f.read()

start_mark = '<!-- VERSION_HISTORY_START -->'
end_mark = '<!-- VERSION_HISTORY_END -->'
pattern = rf'{re.escape(start_mark)}.*?{re.escape(end_mark)}'
replacement = f'{start_mark}\n{new_block}\n    {end_mark}'

if re.search(pattern, html, re.DOTALL):
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)
else:
    # fallback: replace old single-version block
    old_block = r'(<div class="text-center mt-5 pt-5">.*?</div>)'
    html = re.sub(old_block, f'{start_mark}\n{new_block}\n    {end_mark}', html, flags=re.DOTALL)

with open(html_path, 'w') as f:
    f.write(html)
print('✅ home.html 已更新')

# --- 6. git commit + push ---
subprocess.run(['git', 'add', '-A'], check=True, timeout=10)
subprocess.run(['git', 'commit', '-m', f'首页版本号 {new_tag}'], check=True, timeout=10)
subprocess.run(['git', 'push'], check=True, timeout=30)
print('✅ git 已提交推送')

# --- 7. 创建 GitHub Release（中文描述）---
release_notes = []
release_notes.append(f'## v{new_ver} 更新内容\n')
for ver, date, msg in rows:
    release_notes.append(f'- **v{ver}** ({date}) — {msg}')
notes_body = '\n'.join(release_notes)

subprocess.run(['gh', 'release', 'create', new_tag,
                '--title', f'v{new_ver} 版本更新',
                '--notes', notes_body,
                '--repo', 'relover1986/django'], check=True, timeout=30)
print(f'✅ Release {new_tag} 已创建')

# --- 8. pm2 restart ---
subprocess.run(['pm2', 'restart', '0'], check=True, timeout=10)
print('✅ pm2 已重启 DONE')
