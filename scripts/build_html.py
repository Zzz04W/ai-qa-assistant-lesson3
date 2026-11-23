# -*- coding: utf-8 -*-
"""把 03_知识库.json 与 05_规则配置.json 内嵌进单文件问答页。

零外部依赖、零网络请求；生成后双击即可打开。
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>课程智能问答助手 · 第 3 课</title>
<style>
  :root{
    --bg:#f5f7fb; --card:#ffffff; --ink:#1f2937; --muted:#6b7280;
    --line:#e5e7eb; --brand:#2563eb; --brand-soft:#eff6ff;
    --ok:#15803d; --ok-bg:#f0fdf4; --no:#b91c1c; --no-bg:#fef2f2;
    --warn:#b45309; --warn-bg:#fffbeb;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
    line-height:1.7;-webkit-font-smoothing:antialiased}
  .wrap{max-width:880px;margin:0 auto;padding:32px 18px 56px}
  header{margin-bottom:22px}
  .eyebrow{display:inline-block;background:var(--brand-soft);color:var(--brand);
    font-size:12px;font-weight:700;letter-spacing:.06em;padding:5px 12px;border-radius:999px}
  h1{font-size:27px;margin:12px 0 6px;letter-spacing:-.02em}
  .sub{color:var(--muted);font-size:14px;margin:0}
  .card{background:var(--card);border:1px solid var(--line);border-radius:16px;
    padding:22px;box-shadow:0 6px 24px rgba(15,23,42,.05)}
  label{display:block;font-size:13px;font-weight:700;margin-bottom:9px;color:#374151}
  .ask{display:flex;gap:10px}
  input[type=text]{flex:1;min-width:0;padding:13px 15px;font-size:15px;
    border:1px solid #d1d5db;border-radius:10px;background:#fff;color:var(--ink);outline:none}
  input[type=text]:focus{border-color:var(--brand);box-shadow:0 0 0 3px rgba(37,99,235,.12)}
  button{cursor:pointer;font-family:inherit}
  .btn-primary{padding:0 22px;border:0;border-radius:10px;background:var(--brand);color:#fff;
    font-size:15px;font-weight:700;white-space:nowrap;transition:background .15s}
  .btn-primary:hover{background:#1d4ed8}
  .examples{margin-top:18px}
  .examples .t{font-size:12px;color:var(--muted);margin-bottom:9px}
  .chips{display:flex;flex-wrap:wrap;gap:8px}
  .chip{background:#f9fafb;border:1px solid var(--line);color:#374151;border-radius:999px;
    padding:6px 13px;font-size:13px;transition:all .15s}
  .chip:hover{background:var(--brand-soft);border-color:#bfdbfe;color:var(--brand)}
  .result{margin-top:22px}
  .badge{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:700;
    padding:5px 11px;border-radius:999px;margin-bottom:12px}
  .badge.ok{background:var(--ok-bg);color:var(--ok)}
  .badge.no{background:var(--no-bg);color:var(--no)}
  .answer-box{border:1px solid #bbf7d0;background:#fbfffc;border-radius:12px;padding:18px 20px}
  .answer-box.reject{border-color:#fecaca;background:#fffafa}
  .q-echo{font-size:13px;color:var(--muted);margin-bottom:10px}
  .a-text{font-size:16px;font-weight:600;margin:0 0 16px;line-height:1.8}
  .meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;
    border-top:1px dashed var(--line);padding-top:14px}
  .meta div{font-size:12px;color:var(--muted);min-width:0}
  .meta b{display:block;color:#111827;font-size:13px;font-weight:700;margin-top:2px;
    overflow-wrap:anywhere}
  .hit{border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:10px;background:#fff}
  .hit .hid{font-size:12px;color:var(--brand);font-weight:700}
  .hit .hq{font-size:13px;color:var(--muted);margin:3px 0 8px}
  .note{margin-top:12px;background:var(--warn-bg);border:1px solid #fde68a;color:var(--warn);
    border-radius:10px;padding:10px 13px;font-size:13px}
  .empty{margin-top:22px;text-align:center;color:#9ca3af;font-size:14px;padding:26px;
    border:1px dashed var(--line);border-radius:14px}
  footer{margin-top:26px;text-align:center;color:#9ca3af;font-size:12px;line-height:1.9}
  @media(max-width:560px){.wrap{padding:20px 12px 40px}h1{font-size:23px}
    .card{padding:17px}.ask{flex-direction:column}.btn-primary{padding:13px;height:auto}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <span class="eyebrow">课程知识库 · 本地问答</span>
    <h1>AI 智能问答助手</h1>
    <p class="sub">基于《人工智能工具应用实践》课程 FAQ · 可显示命中依据与来源 · 越界会拒答</p>
  </header>

  <section class="card">
    <label for="q">输入你的问题</label>
    <div class="ask">
      <input id="q" type="text" placeholder="例如：课件在哪里下载？" autocomplete="off">
      <button class="btn-primary" id="askBtn">提问</button>
    </div>
    <div class="examples">
      <div class="t">试试这些示例（含别名问法、越界问法与无命中问法）</div>
      <div class="chips" id="chips"></div>
    </div>
    <div id="result" class="result"></div>
  </section>

  <footer>
    本助手基于本地课堂 FAQ，不连接外部大模型。<br>
    全部素材为课堂虚构数据；越界与低置信度问题一律拒答，不编造课程政策。
  </footer>
</div>

<script>
/* ===== 内嵌知识库与规则（由 build_html.py 注入） ===== */
const KB = __KB_JSON__;
const CFG = __CFG_JSON__;

/* ===== 与 scripts/matcher.py 严格同口径的匹配引擎 ===== */
function normalize(s){
  return Array.from(String(s).toLowerCase())
    .filter(ch => /\p{L}|\p{N}/u.test(ch)).join('');
}
function bigrams(s){
  const out = new Set();
  if(s.length >= 2){ for(let i=0;i<s.length-1;i++) out.add(s.slice(i,i+2)); }
  else if(s.length === 1){ out.add(s); }
  return out;
}
function courseTermBigrams(){
  const pool = new Set();
  for(const it of KB.items){
    for(const text of [it.question, ...it.aliases, ...it.tags]){
      for(const g of bigrams(normalize(text))) pool.add(g);
    }
  }
  return pool;
}
function scoreEntry(qn, entry){
  const qb = bigrams(qn);
  let best = 0, matched = '';
  for(const cand of [entry.question, ...entry.aliases]){
    const cn = normalize(cand);
    if(!cn) continue;
    const cb = bigrams(cn);
    let dice = 0;
    if(qb.size && cb.size){
      let inter = 0;
      cb.forEach(g => { if(qb.has(g)) inter++; });
      dice = 2*inter/(qb.size+cb.size);
    }
    const contain = (cn.includes(qn) || qn.includes(cn)) ? 0.30 : 0;
    let tagHits = 0;
    for(const t of entry.tags){
      const tn = normalize(t);
      if(tn.length >= 2 && qn.includes(tn)) tagHits++;
    }
    const kwhit = Math.min(0.15, 0.05*tagHits);
    const score = Math.min(1, dice + contain + kwhit);
    if(score > best){ best = score; matched = cand; }
  }
  return [best, matched];
}
function checkOutOfScope(qn){
  for(const rule of CFG.rules){
    const kws = rule.keywords.map(normalize).filter(Boolean);
    if(!kws.some(k => qn.includes(k))) continue;
    const exempt = (rule.exempt_keywords || []).map(normalize).filter(Boolean);
    if(exempt.length && exempt.some(k => qn.includes(k))) continue;
    return rule;
  }
  if(qn.length < CFG.short_chat.max_chars){
    const pool = courseTermBigrams();
    let hit = false;
    bigrams(qn).forEach(g => { if(pool.has(g)) hit = true; });
    if(!hit) return {rule_id:'V08', fallback:CFG.short_chat.message};
  }
  return null;
}
function answer(q){
  const qn = normalize(q);
  const rule = checkOutOfScope(qn);
  if(rule){
    return {action:'拒答', reason:'out_of_scope', rule_id:rule.rule_id,
            fallback:rule.fallback, hits:[]};
  }
  const scored = KB.items.map(it => {
    const [score, matched] = scoreEntry(qn, it);
    return {score, matched, item:it};
  }).sort((a,b) => b.score - a.score);
  const top = scored.length ? scored[0].score : 0;
  if(!scored.length || top <= 0){
    return {action:'拒答', reason:'no_hit', score:0,
            fallback:CFG.no_hit.message, hits:[]};
  }
  if(top < CFG.threshold){
    return {action:'拒答', reason:'low_confidence', score:top,
            fallback:CFG.low_confidence.message, matched:scored[0].matched, hits:[]};
  }
  const ties = scored.filter(x => Math.abs(x.score - top) < 1e-9);
  const hits = ties.slice(0, CFG.tie.max_items).map(x => ({
    id:x.item.id, score:x.score, matched:x.matched,
    answer:x.item.answer, source:x.item.source, question:x.item.question
  }));
  return {action:'应答', reason:'matched', score:top,
          confidence_note: ties.length > 1 ? CFG.tie.note : '', hits};
}

/* ===== 界面渲染 ===== */
const EXAMPLES = [
  '这门课一共几次课',      // 直接命中
  'PPT 在哪拿',            // 术语别名命中
  '没装 Trae 会不会影响成绩', // 关键词易误伤的边界问法
  '我的成绩是多少',        // 越界拒答 V01
  '考试是几月几号',        // 越界拒答 V05
  '量子纠缠原理是什么'     // 无命中/低置信度
];
function esc(s){
  return String(s).replace(/[&<>"']/g, c =>
    ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function render(question, res){
  const box = document.getElementById('result');
  if(res.action === '拒答'){
    const reasonText = {
      out_of_scope:`越界规则 ${res.rule_id} 命中`,
      low_confidence:`匹配得分 ${res.score.toFixed(2)} < 阈值 ${CFG.threshold}`,
      no_hit:'知识库无命中'
    }[res.reason] || '';
    box.innerHTML = `
      <span class="badge no">已拒答 · 不编造答案</span>
      <div class="answer-box reject">
        <div class="q-echo">问：${esc(question)}</div>
        <p class="a-text">${esc(res.fallback)}</p>
        <div class="meta"><div>判定依据<b>${esc(reasonText)}</b></div>
          <div>处理动作<b>停止匹配，直接拒答</b></div></div>
      </div>`;
    return;
  }
  const cards = res.hits.map(h => `
    <div class="hit">
      <div class="hid">命中条目 ${esc(h.id)}</div>
      <div class="hq">标准问法：${esc(h.question)}</div>
      <p class="a-text" style="margin-bottom:12px">${esc(h.answer)}</p>
      <div class="meta">
        <div>匹配得分<b>${h.score.toFixed(2)}</b></div>
        <div>命中别名/问法<b>${esc(h.matched)}</b></div>
        <div>来源 source<b>${esc(h.source)}</b></div>
      </div>
    </div>`).join('');
  box.innerHTML = `
    <span class="badge ok">已应答 · 命中 ${res.hits.length} 条</span>
    ${cards}
    ${res.confidence_note ? `<div class="note">${esc(res.confidence_note)}：以上条目得分并列，可能需要人工确认。</div>` : ''}`;
}
function ask(question){
  const q = (question || document.getElementById('q').value).trim();
  if(!q) return;
  document.getElementById('q').value = q;
  render(q, answer(q));
}
document.getElementById('askBtn').addEventListener('click', () => ask());
document.getElementById('q').addEventListener('keydown', e => {
  if(e.key === 'Enter') ask();
});
const chips = document.getElementById('chips');
EXAMPLES.forEach(e => {
  const b = document.createElement('button');
  b.className = 'chip'; b.type = 'button'; b.textContent = e;
  b.addEventListener('click', () => ask(e));
  chips.appendChild(b);
});
</script>
</body>
</html>
'''


def main():
    kb = json.load(open(os.path.join(BASE, "03_知识库.json"), encoding="utf-8"))
    cfg = json.load(open(os.path.join(BASE, "05_规则配置.json"), encoding="utf-8"))
    def inject(obj):
        return json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")
    html = TEMPLATE.replace("__KB_JSON__", inject(kb)).replace("__CFG_JSON__", inject(cfg))
    out = os.path.join(BASE, "06_问答助手.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("written:", out, "bytes:", len(html.encode("utf-8")))


if __name__ == "__main__":
    main()
