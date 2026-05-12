from django import template
import re

register = template.Library()

@register.filter
def filter_options(value, qtype):
    """
    过滤选项显示：
    - 单选/多选 → 只保留 ABCDE 字母标签
    - 判断题 → 只显示 对/错
    """
    if not value:
        return ''

    value = str(value).strip()
    qtype = str(qtype).strip()

    if '判断' in qtype:
        # 判断题：只保留 对/错
        parts = re.split(r'[，,、\s]+', value)
        filtered = [p for p in parts if p in ('对', '错')]
        return ' '.join(filtered) if filtered else value

    # 单选/多选：只保留 A B C D E 等字母标签
    labels = re.findall(r'\b([A-E])\s*[.、，,]?\s*(?=[A-E]\s*[.、，,]|$)', value)
    if not labels:
        # 尝试另一种格式: "A.xxx B.xxx C.xxx"
        labels = re.findall(r'([A-E])\s*[.、，,]', value)

    if labels:
        return ' '.join(sorted(set(labels), key=lambda x: 'ABCDE'.index(x)))
    
    # 兜底：提取所有大写字母
    letters = re.findall(r'[A-E]', value)
    if letters:
        return ' '.join(sorted(set(letters), key=lambda x: 'ABCDE'.index(x)))

    return value
