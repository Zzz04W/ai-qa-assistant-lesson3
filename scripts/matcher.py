# -*- coding: utf-8 -*-
"""问答匹配引擎（Python 版）。

与 06_问答助手.html 内嵌的 JS 版严格同口径：
归一化 → 8 条越界规则 → Dice/包含/标签打分 → 阈值与并列处理。
评测脚本和网页共用本文件定义的口径，不做任何标准答案硬编码。
"""


def normalize(s: str) -> str:
    """转小写，仅保留 Unicode 字母与数字，去除空白和标点。"""
    return "".join(ch.lower() for ch in s if ch.isalnum())


def bigrams(s: str) -> set:
    if len(s) >= 2:
        return {s[i:i + 2] for i in range(len(s) - 1)}
    return {s} if s else set()


def score_entry(q_norm: str, entry: dict):
    """返回 (最高得分, 命中的候选问法)。"""
    qb = bigrams(q_norm)
    best, matched = 0.0, ""
    for cand in [entry["question"]] + entry["aliases"]:
        cn = normalize(cand)
        if not cn:
            continue
        cb = bigrams(cn)
        dice = 2 * len(qb & cb) / (len(qb) + len(cb)) if qb and cb else 0.0
        contain = 0.30 if (cn in q_norm or q_norm in cn) else 0.0
        tag_hits = sum(1 for t in entry["tags"]
                       if len(normalize(t)) >= 2 and normalize(t) in q_norm)
        kwhit = min(0.15, 0.05 * tag_hits)
        score = min(1.0, dice + contain + kwhit)
        if score > best:
            best, matched = score, cand
    return best, matched


def course_term_bigrams(kb: dict) -> set:
    """课程术语二元组池，用于 V08「短句且不含课程术语」判定。"""
    pool = set()
    for item in kb["items"]:
        for text in [item["question"]] + item["aliases"] + item["tags"]:
            pool |= bigrams(normalize(text))
    return pool


def check_out_of_scope(q_norm: str, config: dict, kb: dict):
    """返回命中的越界规则 dict；未命中返回 None。"""
    for rule in config["rules"]:
        kws = [normalize(k) for k in rule["keywords"]]
        if not any(k and k in q_norm for k in kws):
            continue
        exempt = [normalize(k) for k in rule.get("exempt_keywords", [])]
        if exempt and any(k and k in q_norm for k in exempt):
            continue
        return rule

    # V08 的第二条判定：短句且不含任何课程术语
    qb = bigrams(q_norm)
    if len(q_norm) < config["short_chat"]["max_chars"] and not (qb & course_term_bigrams(kb)):
        return {"rule_id": "V08", "fallback": config["short_chat"]["message"]}
    return None


def answer(q: str, kb: dict, config: dict) -> dict:
    """完整三步流程，返回结构化结果。"""
    q_norm = normalize(q)
    rule = check_out_of_scope(q_norm, config, kb)
    if rule:
        return {"action": "拒答", "reason": "out_of_scope", "rule_id": rule["rule_id"],
                "fallback": rule["fallback"], "hits": []}

    scored = []
    for item in kb["items"]:
        s, matched = score_entry(q_norm, item)
        scored.append((s, matched, item))
    scored.sort(key=lambda x: -x[0])
    top = scored[0][0] if scored else 0.0

    if not scored or top <= 0:
        return {"action": "拒答", "reason": "no_hit", "fallback": config["no_hit"]["message"],
                "score": 0.0, "hits": []}
    if top < config["threshold"]:
        return {"action": "拒答", "reason": "low_confidence", "score": top,
                "fallback": config["low_confidence"]["message"],
                "matched": scored[0][1], "hits": []}

    ties = [x for x in scored if abs(x[0] - top) < 1e-9]
    hits = []
    for s, matched, item in ties[:config["tie"]["max_items"]]:
        hits.append({"id": item["id"], "score": s, "matched": matched,
                     "answer": item["answer"], "source": item["source"],
                     "question": item["question"]})
    result = {"action": "应答", "reason": "matched", "score": top,
              "confidence_note": config["tie"]["note"] if len(ties) > 1 else "", "hits": hits}
    return result
