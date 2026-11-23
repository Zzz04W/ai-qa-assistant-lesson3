// 从 06_问答助手.html 抽取内嵌匹配引擎，与 Python 版对拍。
const fs = require('fs');
const path = require('path');
const base = path.dirname(__dirname);
const html = fs.readFileSync(path.join(base, '06_问答助手.html'), 'utf8');
const start = html.indexOf('const KB = ');
const end = html.indexOf('/* ===== 界面渲染 ===== */');
if (start < 0 || end < 0) throw new Error('cannot locate embedded engine');
const engine = html.slice(start, end);
const sandbox = {};
const fn = new Function(engine + '\nreturn {answer, normalize, scoreEntry};');
const api = fn();

const evalCsv = path.join(path.dirname(base), '素材包', '最热AI应用实践课', '第3课_问答助手', '04_评测集.csv');
const lines = fs.readFileSync(evalCsv, 'utf8').replace(/^\uFEFF/, '').trim().split(/\r?\n/);
// 极简 CSV 解析：按逗号切分，合并双引号内的字段
function parseCsvLine(line) {
  const cols = []; let cur = '', quoted = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (c === '"') {
      if (quoted && line[i + 1] === '"') { cur += '"'; i++; }
      else quoted = !quoted;
    } else if (c === ',' && !quoted) { cols.push(cur); cur = ''; }
    else cur += c;
  }
  cols.push(cur);
  return cols;
}
const out = [];
for (let i = 1; i < lines.length; i++) {
  const cols = parseCsvLine(lines[i]);
  const q = cols[2];
  const r = api.answer(q);
  out.push({
    q,
    action: r.action,
    ids: r.hits.map(h => h.id).join(';'),
    score: r.score === undefined ? '' : Number(r.score).toFixed(2),
    reason: r.reason,
    rule: r.rule_id || ''
  });
}
console.log(JSON.stringify(out, null, 2));
