"""项目B 第1步：清洗 Disneyland 评论数据。
运行：python scripts/b1_clean.py
输入：data/raw/DisneylandReviews.csv（文件名以你下载的为准，需要时改下面的 RAW）
输出：data/clean_reviews.csv、output/b1_clean_log.csv
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "DisneylandReviews.csv"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(RAW, encoding="latin-1")          # 该文件不是 utf-8，必须指定编码
df = df.rename(columns={"Disneyland_Branch": "Branch"})   # 兼容不同版本的列名
need = ["Review_ID", "Rating", "Year_Month", "Reviewer_Location", "Review_Text", "Branch"]
missing_cols = [c for c in need if c not in df.columns]
assert not missing_cols, f"缺少列：{missing_cols}，当前列：{list(df.columns)}"

raw_n = len(df)
log = [("原始行数", 0, raw_n)]
print("原始行数：", f"{raw_n:,}")

# 1) Year_Month 缺失：置空但保留该行（评论和评分仍有用）
is_missing = df["Year_Month"].astype(str).str.strip().str.lower().eq("missing") | df["Year_Month"].isna()
ym_missing = int(is_missing.sum())
df.loc[is_missing, "Year_Month"] = pd.NA
log.append(("Year_Month 缺失（置空，保留该行）", ym_missing, len(df)))
df["year"] = pd.to_numeric(df["Year_Month"].astype("string").str.split("-").str[0], errors="coerce")

def step(name, new_df):
    global df
    log.append((name, len(df) - len(new_df), len(new_df)))
    df = new_df

# 2) 重复
dup_id = int(df.duplicated("Review_ID").sum())
dup_text = int(df.drop_duplicates("Review_ID").duplicated("Review_Text").sum())
print(f"Review_ID 重复：{dup_id}；去掉 ID 重复后正文重复：{dup_text}")
step("删除 Review_ID 重复", df.drop_duplicates("Review_ID"))
step("删除评论正文完全重复", df.drop_duplicates("Review_Text"))

# 3) 空文本 / 过短文本（少于 5 个词）
words = df["Review_Text"].fillna("").astype(str).str.split().str.len()
step("删除空文本或少于5个词的评论", df[words >= 5])

# 4) 评分合法性
step("删除评分不在 1-5 的行", df[df["Rating"].between(1, 5)])

df.to_csv(ROOT / "data" / "clean_reviews.csv", index=False)
log_df = pd.DataFrame(log, columns=["步骤", "涉及行数", "剩余行数"])
log_df["占原始%"] = (log_df["涉及行数"] / raw_n * 100).round(2)
log_df.to_csv(OUT / "b1_clean_log.csv", index=False, encoding="utf-8-sig")
print(log_df.to_string(index=False))
print(f"\n有效样本：{len(df):,} 条，占原始 {len(df)/raw_n*100:.2f}%")
