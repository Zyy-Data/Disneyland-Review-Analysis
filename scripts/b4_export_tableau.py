"""项目B 第4步：合并清洗数据与AI标注，导出给 Tableau 的小表，并统计差评主题。
运行：python scripts/b4_export_tableau.py v2      （版本=你最终采用的、覆盖500条的标注版本）
输出：output/tableau_b/*.csv
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
T = OUT / "tableau_b"
T.mkdir(exist_ok=True)
ver = sys.argv[1] if len(sys.argv) > 1 else "v1"

s = pd.read_csv(OUT / "b3_sample500.csv")
ai = pd.read_csv(OUT / f"ai_labels_{ver}.csv")
m = s.merge(ai, on="id", how="left")
assert m["sentiment"].notna().all(), f"版本 {ver} 没有覆盖全部500条，请先对全部500条标注"

# 差评主题
neg = m[m["sentiment"] == "negative"]
cnt = (neg["topics"].fillna("").str.split("|").explode().str.strip()
          .replace("", pd.NA).dropna().value_counts().reset_index())
cnt.columns = ["topic", "negative_reviews_mentioning"]
cnt["share_of_negative_%"] = (cnt["negative_reviews_mentioning"] / len(neg) * 100).round(1)
cnt.to_csv(T / "negative_topics.csv", index=False, encoding="utf-8-sig")
print(f"500 条样本中 AI 判定差评 {len(neg)} 条（{len(neg)/len(m)*100:.1f}%）")
print(cnt.to_string(index=False))

# 情感 x 评分 交叉（发现 AI 与星级矛盾的条目，便于挑典型评论）
print("\n情感 x 星级：\n", pd.crosstab(m["sentiment"], m["Rating"]).to_string())
m[(m["sentiment"] == "negative") & (m["Rating"] >= 4)][["id", "Rating", "Review_Text", "evidence"]].to_csv(
    T / "negative_but_high_rating.csv", index=False, encoding="utf-8-sig")

# 导出给 Tableau 的底表
m[["id", "Branch", "Rating", "year", "Reviewer_Location", "sentiment", "topics"]].to_csv(
    T / "sample500_labeled.csv", index=False, encoding="utf-8-sig")
for name in ["b2_branch_summary.csv", "b2_rating_dist_pct.csv", "b2_year_counts.csv",
             "b2_location_top5.csv", "b2_location_top5_by_branch.csv"]:
    pd.read_csv(OUT / name).to_csv(T / name.replace("b2_", ""), index=False, encoding="utf-8-sig")
print("已导出到", T)
