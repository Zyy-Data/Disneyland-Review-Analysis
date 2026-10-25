"""项目B 第2步：三个园区评分、年度评论量、来源国家 TOP5。
运行：python scripts/b2_stats.py
输出：output/b2_*.csv 与 output/b2_avg_rating.png
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
df = pd.read_csv(ROOT / "data" / "clean_reviews.csv")

# 1) 各园区评论数、平均分
by_branch = df.groupby("Branch").agg(评论数=("Rating", "size"), 平均分=("Rating", "mean")).round(2).reset_index()
by_branch.to_csv(OUT / "b2_branch_summary.csv", index=False, encoding="utf-8-sig")
print(by_branch.to_string(index=False))
assert by_branch["评论数"].sum() == len(df), "三园区评论数之和应等于有效样本"

# 2) 评分分布（各园区内占比，加总100%）
dist = (df.groupby(["Branch", "Rating"]).size().unstack(fill_value=0))
dist_pct = (dist.div(dist.sum(axis=1), axis=0) * 100).round(2)
dist_pct.stack().reset_index(name="占比%").to_csv(OUT / "b2_rating_dist_pct.csv", index=False, encoding="utf-8-sig")   # 长表，方便 Tableau
print("\n评分占比%（每行加总100）：\n", dist_pct.to_string())

# 3) 年度评论量
yearly = (df.dropna(subset=["year"]).astype({"year": int})
            .groupby(["year", "Branch"]).size().reset_index(name="评论数"))
yearly.to_csv(OUT / "b2_year_counts.csv", index=False, encoding="utf-8-sig")

# 4) 来源国家 TOP5（总体 + 各园区）
top_all = df["Reviewer_Location"].value_counts().head(5).reset_index()
top_all.columns = ["国家", "评论数"]
top_all.to_csv(OUT / "b2_location_top5.csv", index=False, encoding="utf-8-sig")
print("\n来源国家 TOP5（总体）：\n", top_all.to_string(index=False))
rows = []
for b, g in df.groupby("Branch"):
    for loc, n in g["Reviewer_Location"].value_counts().head(5).items():
        rows.append((b, loc, n))
pd.DataFrame(rows, columns=["Branch", "国家", "评论数"]).to_csv(
    OUT / "b2_location_top5_by_branch.csv", index=False, encoding="utf-8-sig")

# 5) 小图（英文标签）
plt.figure(figsize=(5, 3))
plt.bar(by_branch["Branch"].str.replace("Disneyland_", ""), by_branch["平均分"])
plt.ylim(1, 5); plt.ylabel("mean rating"); plt.tight_layout()
plt.savefig(OUT / "b2_avg_rating.png", dpi=150)
