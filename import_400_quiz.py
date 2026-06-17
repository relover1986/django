#!/usr/bin/env python3
"""解析 400题.docx → 入库 MySQL app01_question，类别=安全"""
import re, sys, os
import docx
import pymysql

DOCX_PATH = "/Users/sunhongchen/.hermes/cache/documents/doc_293f3f1d1cbb_400题.docx"
CATEGORY = "安全"

# ========== MySQL 连接 ==========
DB_CONFIG = dict(
    host="bxks.online", port=3306, user="lnjx", password="lnjx613811",
    database="lnjx", charset="utf8mb4"
)

# ========== 解析 docx ==========
doc = docx.Document(DOCX_PATH)
lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

# 确定各题型段落范围
sec_breaks = {}
for i, t in enumerate(lines):
    if "单项选择题" in t:
        sec_breaks["单选题"] = i
    elif "多项选择题" in t:
        sec_breaks["多选题"] = i
    elif "判断题" in t:
        sec_breaks["判断题"] = i

sections = []
for qtype in ["单选题", "多选题", "判断题"]:
    start = sec_breaks.get(qtype)
    end = None
    for other, pos in sorted(sec_breaks.items()):
        if pos > start:
            end = pos
            break
    sections.append((qtype, start, end))

# ========== 逐题解析 ==========
questions = []

for qtype, start, end in sections:
    body = lines[start+1:end] if end else lines[start+1:]
    
    if qtype == "判断题":
        # 每行一个判断题: 题目文本。（A）或 （B）
        for line in body:
            m = re.search(r'[（(]([AB])[）)]$', line)
            if not m:
                continue
            answer = m.group(1)
            question_text = line[:m.start()].strip()
            questions.append({
                "category": CATEGORY,
                "question_type": "判断题",
                "tihao": "",
                "question": question_text,
                "options": "A.对 B.错",
                "correct_answer": answer,
            })
    
    elif qtype in ("单选题", "多选题"):
        i = 0
        tihao = 0
        while i < len(body):
            line = body[i]
            # 检查是不是题目行（以（答案）结尾）
            m = re.search(r'[（(]([A-E]+)[）)]$', line)
            if m:
                answer = m.group(1)
                question_text = line[:m.start()].strip()
                # 选项：收集后续行直到碰到下一个题目行
                opt_lines = []
                while i + 1 < len(body):
                    next_line = body[i + 1]
                    # 如果下一行以选项字母开头，或是选项的延续（C. D.）
                    if re.match(r'^[A-E][.、．]', next_line):
                        opt_lines.append(next_line)
                        i += 1
                    elif re.search(r'[（(][A-E]+[）)]$', next_line):
                        # 下一个题目行，停止
                        break
                    else:
                        # 可能前一行的选项续行（如C.D.开头无A.）
                        opt_lines.append(next_line)
                        i += 1
                        break
                
                # 合并选项
                if opt_lines:
                    # 合并所有选项行，按 A. B. C. D. 分割
                    all_opts = " ".join(opt_lines)
                    # 标准化分隔：A.xxx B.xxx C.xxx D.xxx
                    opts = re.sub(r'\s+', ' ', all_opts)
                else:
                    opts = ""
                
                tihao += 1
                questions.append({
                    "category": CATEGORY,
                    "question_type": qtype,
                    "tihao": str(tihao),
                    "question": question_text,
                    "options": opts,
                    "correct_answer": answer,
                })
                i += 1
            else:
                i += 1

print(f"解析完成: {len(questions)} 题")
for qt in ["单选题", "多选题", "判断题"]:
    cnt = sum(1 for q in questions if q["question_type"] == qt)
    print(f"  {qt}: {cnt}")

# ========== 去重 + 入库 ==========
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()

# 先查已有题目（类别=安全）
cur.execute("SELECT question FROM app01_question WHERE category=%s", (CATEGORY,))
existing = set(row[0] for row in cur.fetchall())
print(f"已有「{CATEGORY}」题目: {len(existing)} 条")

new_qs = [q for q in questions if q["question"] not in existing]
print(f"新题: {len(new_qs)} 条")

if new_qs:
    import time
    now = int(time.time())
    sql = """INSERT INTO app01_question 
             (category, question_type, tihao, question, `options`, correct_answer, analysis)
             VALUES (%s, %s, %s, %s, %s, %s, '')"""
    vals = []
    for q in new_qs:
        vals.append((q["category"], q["question_type"], q["tihao"], q["question"], q["options"], q["correct_answer"]))
    cur.executemany(sql, vals)
    conn.commit()
    print(f"✅ 入库 {cur.rowcount} 条")
else:
    print("✅ 全部已存在，无新题")

cur.close()
conn.close()
