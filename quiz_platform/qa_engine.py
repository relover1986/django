import json, os
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI

_BASE = os.path.dirname(os.path.abspath(__file__))
VECTOR_LECTURE = os.path.join(_BASE, "vector_store_lecture.json")
VECTOR_TEXTBOOK = os.path.join(_BASE, "vector_store_textbook.json")

SILICONFLOW_API_KEY="sk-ijwplxjagzxbtmlugxhbdxtauueiqqwwadgtbdidkkmtfawe"

_client = OpenAI(api_key=SILICONFLOW_API_KEY, base_url="https://api.siliconflow.cn/v1", max_retries=2)
_CHAT_MODELS = ["Qwen/Qwen3-8B", "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "THUDM/GLM-Z1-9B-0414"]
_model_index = 0

def _next_model():
    global _model_index
    m = _CHAT_MODELS[_model_index % len(_CHAT_MODELS)]
    _model_index += 1
    return m

_lecture_chunks, _textbook_chunks = [], []
_vectorizer, _tfidf_matrix = None, None

def _load_stores():
    global _lecture_chunks, _textbook_chunks, _vectorizer, _tfidf_matrix
    if _lecture_chunks:
        return
    with open(VECTOR_LECTURE, "r", encoding="utf-8") as f:
        _lecture_chunks = json.load(f)
    with open(VECTOR_TEXTBOOK, "r", encoding="utf-8") as f:
        _textbook_chunks = json.load(f)
    all_chunks = _lecture_chunks + _textbook_chunks
    texts = [c["snippet"] for c in all_chunks]
    _vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), analyzer="char_wb", token_pattern=None)
    _tfidf_matrix = _vectorizer.fit_transform(texts)
    for c in _lecture_chunks:
        c["_source"] = "讲课-教辅"
    for c in _textbook_chunks:
        c["_source"] = "章节文本"

def search(query: str, top_k: int = 5) -> List[Dict]:
    _load_stores()
    all_chunks = _lecture_chunks + _textbook_chunks
    q_vec = _vectorizer.transform([query])
    scores = cosine_similarity(q_vec, _tfidf_matrix).flatten()
    top_indices = scores.argsort()[::-1][:top_k]
    results = []
    for idx in top_indices:
        if scores[idx] < 0.01:
            continue
        c = all_chunks[idx]
        results.append({"snippet": c["snippet"], "path": c.get("relative", c.get("path", "")),
                        "fname": c.get("fname", ""), "source": c.get("_source", ""),
                        "score": round(float(scores[idx]), 4)})
    return results

def ask(question: str, top_k: int = 5) -> Dict[str, Any]:
    chunks = search(question, top_k=top_k)
    if not chunks:
        return {"answer": "抱歉，知识库中没有找到相关的参考资料。", "sources": [], "model": ""}
    context_parts = []
    for i, c in enumerate(chunks, 1):
        tag = f"[{c['source']}] {c['fname']}"
        context_parts.append(f"--- 参考资料 {i}: {tag} ---\n{c['snippet']}")
    context = "\n\n".join(context_parts)
    system_prompt = ("你是一级建造师（矿业工程）考试的智能助教。"
                     "请根据提供的参考资料回答问题。"
                     "如果参考资料不足以回答，请如实说不知道，不要编造。"
                     "回答时请引用参考资料的来源文件名。"
                     "用中文回答，语言简洁、条理清晰。")
    user_prompt = f"【参考资料】\n{context}\n\n【问题】\n{question}"
    model = _next_model()
    try:
        resp = _client.chat.completions.create(
            model=model, messages=[{"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}],
            max_tokens=2048, temperature=0.3, timeout=120)
        answer = (resp.choices[0].message.content or "").strip()
    except Exception as e:
        answer = f"调用 AI 出错：{type(e).__name__}: {str(e)}"
    return {"answer": answer, "sources": [{"name": f"[{c['source']}] {c['fname']}", "path": c["path"], "score": c["score"]} for c in chunks], "model": model}
