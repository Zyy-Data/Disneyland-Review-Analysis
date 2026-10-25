"""项目B 第3步（上）：抽样 + 生成可直接粘贴给 AI 的分批文件 + 人工盲标表。
运行：
  python scripts/b3_ai_sample.py v1 all       # 用 prompts/prompt_v1.txt，500条分批
  python scripts/b3_ai_sample.py v2 manual    # 用 prompts/prompt_v2.txt，只重跑要人工核对的100条
  python scripts/b3_ai_sample.py v2 all       # 用 prompts/prompt_v2.txt，500条全部重跑
输出：output/b3_sample500.csv、output/b3_manual_sheet.csv（人工盲标表，只生成一次）、
      output/batches_<版本>_<范围>/batch_XX.txt
"""
import sys, json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
scope = sys.argv[2] if len(sys.argv) > 2 else "all"
BATCH, MAXCHARS = 25, 600

df = pd.read_csv(ROOT / "data" / "clean_reviews.csv")
sample = df.sample(500, random_state=42).reset_index(drop=True)      # 固定随机种子，保证可复现
sample.insert(0, "id", range(1, 501))
sample.to_csv(OUT / "b3_sample500.csv", index=False)

manual_ids = sorted(sample.sample(100, random_state=7)["id"].tolist())
sheet = OUT / "b3_manual_sheet.csv"
if not sheet.exists():                                              # 已填写的表不覆盖
    ms = sample[sample["id"].isin(manual_ids)][["id", "Review_Text"]].copy()
    ms["human_sentiment"] = ""      # positive / neutral / negative
    ms["human_topics"] = ""         # 用 | 分隔，如 queue|crowd；没有主题留空
    ms.to_csv(sheet, index=False, encoding="utf-8-sig")
    print("已生成人工盲标表：", sheet)
else:
    print("人工盲标表已存在，未覆盖：", sheet)

raw_prompt = (ROOT / "prompts" / f"prompt_{ver}.txt").read_text(encoding="utf-8")
prompt = "\n".join(l for l in raw_prompt.splitlines() if not l.startswith("（"))   # 去掉说明行
use = sample if scope == "all" else sample[sample["id"].isin(manual_ids)]
outdir = OUT / f"batches_{ver}_{scope}"
outdir.mkdir(exist_ok=True)
rows = [{"id": int(r.id), "text": str(r.Review_Text)[:MAXCHARS]} for r in use.itertuples()]
n = 0
for i in range(0, len(rows), BATCH):
    n += 1
    body = json.dumps(rows[i:i + BATCH], ensure_ascii=False)
    (outdir / f"batch_{n:02d}.txt").write_text(prompt.strip() + "\n\n评论：\n" + body, encoding="utf-8")
print(f"已生成 {n} 个批次文件到 {outdir}，共 {len(rows)} 条评论")
print(f"下一步：逐个把批次文件内容粘贴给 AI，把 AI 返回的 JSON 存到 output/ai_output/{ver}/batch_XX.json")
