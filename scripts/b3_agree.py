"""项目B 第3步（下）：计算 AI 标注与人工盲标的一致率，并列出不一致的条目。
运行：python scripts/b3_agree.py v1
前提：output/b3_manual_sheet.csv 里 human_sentiment / human_topics 已由你自己填写（先别看AI标签！）
输出：output/b3_disagreements_<版本>.csv
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
ver = sys.argv[1] if len(sys.argv) > 1 else "v1"

man = pd.read_csv(OUT / "b3_manual_sheet.csv")
man = man[man["human_sentiment"].astype(str).str.strip().ne("") & man["human_sentiment"].notna()].copy()
ai = pd.read_csv(OUT / f"ai_labels_{ver}.csv")
m = man.merge(ai, on="id", how="inner")
assert len(m) > 0, "没有可比较的条目：确认人工表已填写，且 AI 标注覆盖了这些 id"

def tset(x):
    if pd.isna(x): return frozenset()
    return frozenset(t.strip().lower() for t in str(x).split("|") if t.strip() and t.strip().lower() != "none")

m["human_sentiment"] = m["human_sentiment"].str.strip().str.lower()
m["sent_ok"] = m["human_sentiment"] == m["sentiment"]
m["topic_ok"] = [tset(a) == tset(b) for a, b in zip(m["human_topics"], m["topics"])]

n = len(m)
print(f"版本 {ver}：可比较条数 {n}")
print(f"情感一致率：{m['sent_ok'].mean()*100:.1f}%（{int(m['sent_ok'].sum())}/{n}）")
print(f"主题完全一致率：{m['topic_ok'].mean()*100:.1f}%（{int(m['topic_ok'].sum())}/{n}，主题集合必须完全相同才算一致）")
print("\n情感混淆表（行=人工，列=AI）：")
print(pd.crosstab(m["human_sentiment"], m["sentiment"]).to_string())

bad = m[~(m["sent_ok"] & m["topic_ok"])][["id", "Review_Text", "human_sentiment", "sentiment",
                                          "human_topics", "topics", "evidence"]]
bad.to_csv(OUT / f"b3_disagreements_{ver}.csv", index=False, encoding="utf-8-sig")
print(f"\n不一致条目 {len(bad)} 条，已存到 b3_disagreements_{ver}.csv；逐条看一遍，归类错误类型（反讽/混合情感/否定句/主题误判），再据此改提示词")
