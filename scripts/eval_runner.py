# -*- coding: utf-8 -*-
"""20 题标准评测集跑分脚本。

口径与 06_问答助手.html 内嵌 JS 完全相同（见 scripts/matcher.py）。
数字全部由脚本计算，不手工填写，不把标准答案硬编码进匹配逻辑。

用法：
  python eval_runner.py --out 08_评测结果.csv --stats 08_统计.json
"""
import argparse
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matcher import answer, normalize

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAT_EVAL = os.path.join(os.path.dirname(BASE), "素材包", "最热AI应用实践课",
                        "第3课_问答助手", "04_评测集.csv")


def expected_rule(standard: str):
    m = re.search(r"按\s*(V\d\d)\s*拒答", standard or "")
    return m.group(1) if m else ""


def classify(row, res):
    exp, got = row["期望处理"], res["action"]
    if exp == got:
        if exp == "应答":
            ids = [h["id"] for h in res["hits"]]
            if row["期望条目id"] and row["期望条目id"] not in ids:
                return False, "命中条目错误"
        else:
            er = expected_rule(row["标准答案或标准处理"])
            if er and res.get("rule_id") != er:
                return False, "越界规则错配"
        return True, ""
    if exp == "应答":
        reason = res.get("reason")
        if reason == "out_of_scope":
            return False, "越界规则误伤"
        if reason == "no_hit":
            return False, "无命中"
        if reason == "low_confidence":
            return False, "别名缺失/匹配分不足"
    return False, "越界漏判"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "08_评测结果.csv"))
    ap.add_argument("--stats", default=os.path.join(BASE, "08_统计.json"))
    args = ap.parse_args()

    kb = json.load(open(os.path.join(BASE, "03_知识库.json"), encoding="utf-8"))
    config = json.load(open(os.path.join(BASE, "05_规则配置.json"), encoding="utf-8"))
    rows = list(csv.DictReader(open(MAT_EVAL, encoding="utf-8-sig")))

    out_rows = []
    for row in rows:
        res = answer(row["问题"], kb, config)
        correct, err = classify(row, res)
        out_rows.append({
            "题号": row["题号"],
            "问题": row["问题"],
            "期望处理(应答/拒答)": row["期望处理"],
            "期望条目id": row["期望条目id"],
            "实际处理": res["action"],
            "实际条目id": ";".join(h["id"] for h in res["hits"]),
            "匹配得分": f"{res['score']:.2f}" if "score" in res else "",
            "是否正确": "正确" if correct else "错误",
            "错误类型": err,
        })

    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    ans = [r for r in out_rows if r["期望处理(应答/拒答)"] == "应答"]
    rej = [r for r in out_rows if r["期望处理(应答/拒答)"] == "拒答"]
    a_ok = sum(r["是否正确"] == "正确" for r in ans)
    r_ok = sum(r["是否正确"] == "正确" for r in rej)
    t_ok = a_ok + r_ok
    stats = {
        "应答准确率": {"分子": a_ok, "分母": len(ans),
                   "百分比": round(100 * a_ok / len(ans), 2)},
        "拒答正确率": {"分子": r_ok, "分母": len(rej),
                   "百分比": round(100 * r_ok / len(rej), 2)},
        "总体正确率": {"分子": t_ok, "分母": len(out_rows),
                   "百分比": round(100 * t_ok / len(out_rows), 2)},
        "错题": [{"题号": r["题号"], "问题": r["问题"], "错误类型": r["错误类型"]}
               for r in out_rows if r["是否正确"] == "错误"],
    }
    with open(args.stats, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
