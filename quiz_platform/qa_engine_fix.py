import os
path = "/root/django/quiz_platform/qa_engine.py"
with open(path) as f:
    content = f.read()
content = content.replace(
    "SILICONFLOW_API_KEY=\"***\"",
    "SILICONFLOW_API_KEY = os.environ.get(\"SILICONFLOW_API_KEY\", \"\")"
)
with open(path, "w") as f:
    f.write(content)
print("Fixed ✅")
