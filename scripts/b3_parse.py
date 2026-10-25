"""项目B 第3步（中）：把 AI 返回的 JSON 合并成一张表，并检查格式。
运行：python scripts/b3_parse.py v1
输入：output/ai_output/<版本>/*.json（或 .txt），每个文件是 AI 对一个批次的原样回复
输出：output/ai_labels_<版本>.csv
"""
import sys, json, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
SENT = {"positive", "neutral", "negative"}
TOPICS = {"queue", "price", "food", "rides_facilities", "staff_service", "crowd", "other"}

files = sorted(list((OUT / "ai_output" / ver).glob("*.json")) + list((OUT / "ai_output" / ver).glob("*.txt")))
assert files, f"没有找到文件：{OUT / 'ai_output' / ver}"

recs, problems = [], []
for f in files:
    text = f.read_text(encoding="utf-8")
    m = re.search(r"\[.*\]", text, flags=re.S)          # 取第一个 [ 到最后一个 ] ，容忍AI多说的话
    if not m:
        problems.append(f"{f.name}：找不到 JSON 数组"); continue
    try:
        items = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        problems.append(f"{f.name}：JSON 解析失败 {e}"); continue
    for it in items:
        s = str(it.get("sentiment", "")).strip().lower()
        t = [str(x).strip().lower() for x in (it.get("topics") or [])]
        if s not in SENT: problems.append(f"{f.name} id={it.get('id')}：sentiment 非法 '{s}'")
        bad = [x for x in t if x not in TOPICS]
        if bad: problems.append(f"{f.name} id={it.get('id')}：topics 非法 {bad}")
        recs.append({"id": int(it["id"]), "sentiment": s, "topics": "|".join(sorted(set(t))),
                     "evidence": it.get("evidence", "")})

lab = pd.DataFrame(recs)
dup = lab["id"].duplicated().sum()
if dup: problems.append(f"有 {dup} 个重复 id（保留最后一个）"); lab = lab.drop_duplicates("id", keep="last")
lab.sort_values("id").to_csv(OUT / f"ai_labels_{ver}.csv", index=False, encoding="utf-8-sig")
print(f"共解析 {len(lab)} 条标注，来自 {len(files)} 个文件")
print("情感分布：\n", lab["sentiment"].value_counts().to_string())
if problems:
    print("\n发现问题（请回到对应批次让 AI 重新输出）：")
    for p in problems[:30]: print(" -", p)
else:
    print("格式检查通过")
