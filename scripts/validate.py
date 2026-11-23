# -*- coding: utf-8 -*-
"""第 3 步与第 9 步校验：JSON 可解析、id 唯一、别名无冲突、
answer 与规范问答集逐条一致、评测结果行数、文件树完整性。
"""
import csv
import json
import os
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAT = os.path.join(os.path.dirname(BASE), "素材包", "最热AI应用实践课", "第3课_问答助手")

REQUIRED = [
    "01_语料体检报告.md", "02_规范问答集.csv", "03_知识库.json",
    "04_拒答规则.md", "05_规则配置.json", "06_问答助手.html",
    "07_评测报告.md", "08_评测结果.csv", "09_维护与对接说明.md",
    "10_制作说明.md", "11_自评得分表.md",
]


def main():
    kb = json.load(open(os.path.join(BASE, "03_知识库.json"), encoding="utf-8"))
    cfg = json.load(open(os.path.join(BASE, "05_规则配置.json"), encoding="utf-8"))
    nq = list(csv.DictReader(open(os.path.join(BASE, "02_规范问答集.csv"), encoding="utf-8-sig")))
    norm = {r["qid"]: r for r in nq}
    items = kb["items"]

    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), "id 重复"
    alias_map = {}
    conflicts = []
    for i in items:
        for a in i["aliases"]:
            if a in alias_map:
                conflicts.append((a, alias_map[a], i["id"]))
            alias_map[a] = i["id"]
    bad_answer = []
    for i in items:
        qid = i["id"]
        if qid not in norm:
            bad_answer.append((qid, "qid 不存在于规范问答集"))
        elif i["answer"] != norm[qid]["answer"]:
            bad_answer.append((qid, "answer 与规范问答集不一致"))
        if not (2 <= len(i["aliases"]) <= 4):
            bad_answer.append((qid, "aliases 数量不在 2—4"))
        if not (1 <= len(i["tags"]) <= 3):
            bad_answer.append((qid, "tags 数量不在 1—3"))
        if i["scope"] not in ("课程内容", "作业提交", "工具使用", "平台操作"):
            bad_answer.append((qid, "scope 取值非法"))

    ev = list(csv.reader(open(os.path.join(BASE, "08_评测结果.csv"), encoding="utf-8-sig")))
    assert len(ev) == 21, f"评测结果应为 21 行（表头+20题），实际 {len(ev)}"

    missing = [f for f in REQUIRED if not os.path.exists(os.path.join(BASE, f))]
    print(json.dumps({
        "JSON可解析": True,
        "知识条目数": len(items),
        "id唯一": True,
        "别名冲突数": len(conflicts),
        "别名冲突明细": conflicts,
        "answer与规范问答集逐条一致": not bad_answer,
        "字段问题明细": bad_answer,
        "越界规则数": len(cfg["rules"]),
        "阈值": cfg["threshold"],
        "评测结果行数": len(ev),
        "评测结果数据行": len(ev) - 1,
        "必需文件缺失": missing,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
