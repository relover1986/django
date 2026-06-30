#!/usr/bin/env python3
"""插入新版 badge 到 home.html

用法:
  python3 scripts/insert_badge.py <version> <date> <description>

示例:
  python3 scripts/insert_badge.py v1.18 2026-06-18 "新增：题库批量导入功能"

效果:
  在 <!-- VERSION_HISTORY_START --> 后插入新 badge div，
  新版本在最上面，旧版本自动下移。
"""

import re
import sys


def insert_badge(html_path: str, version: str, date: str, description: str) -> None:
    with open(html_path, 'r') as f:
        content = f.read()

    new_badge = f'''                                    <!-- VERSION_HISTORY_START -->
                                    <div class="text-center mt-3">
                                        <p class="lead" style="font-size:1.3rem;">
                                            <span class="badge bg-primary fs-6 me-2">{version}</span>
                                            <span class="text-muted">{date}</span>
                                        </p>
                                        <p class="text-muted" style="font-size:1.0rem;">{description}</p>
                                    </div>

                                    <div class="text-center mt-3">'''

    # 替换锚点后的第一个 div 开头
    anchor = '<!-- VERSION_HISTORY_START -->\n                                    <div class="text-center mt-3">'
    if anchor not in content:
        print(f"错误：未找到锚点 '{anchor}'", file=sys.stderr)
        sys.exit(1)

    content = content.replace(anchor, new_badge, 1)

    with open(html_path, 'w') as f:
        f.write(content)

    print(f"✓ badge {version} ({date}) 已插入")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(f"用法: {sys.argv[0]} <version> <date> <description>", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    date = sys.argv[2]
    description = sys.argv[3]

    insert_badge('/root/django/app01/templates/home.html', version, date, description)
