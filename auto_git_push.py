#!/usr/bin/env python3
"""每日自动提交推送 Django 项目变更到 GitHub"""
import subprocess, os, sys
from datetime import datetime

PROJECT = '/root/django'
os.chdir(PROJECT)

# 1. 检查是否有变更
result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
if not result.stdout.strip():
    print(f'{datetime.now():%Y-%m-%d %H:%M} - 无变更，跳过')
    sys.exit(0)

# 2. add + commit + push
changed = result.stdout.strip().count('\n')
date = datetime.now().strftime('%Y-%m-%d %H:%M')
subprocess.run(['git', 'add', '-A'], check=True)
subprocess.run(['git', 'commit', '-m', f'[auto] 服务器自动备份 {date} ({changed} 文件变更)'], check=True)
subprocess.run(['git', 'push', 'origin', 'master'], check=True)
print(f'{datetime.now():%Y-%m-%d %H:%M} - ✅ 已提交推送 {changed} 个文件')
