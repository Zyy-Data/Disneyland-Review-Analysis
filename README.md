# Disneyland Reviews Analysis (迪士尼三园区游客口碑分析)

## 📌 项目背景
基于 Kaggle 公开数据集（TripAdvisor 评论，约 4.2 万条），旨在探索三个迪士尼园区（加州、巴黎、香港）的游客口碑差异，并挖掘差评核心痛点。

## 🛠️ 技术栈
- **数据处理**：Python (pandas)
- **可视化**：Tableau
- **AI 辅助**：大语言模型 (LLM) 辅助情感与主题标注

## 🚀 核心流程与发现
1. **数据清洗**：使用 pandas 剔除缺失值与重复值，保留有效样本 42,623 条（占原始数据 99.92%）。
2. **基础统计**：加州评分最高 (4.41)，巴黎最低 (3.96)；美国与英国是主要评论来源地。
3. **AI 辅助标注与人机校验**：随机抽取 500 条评论，人工盲标 100 条作为基准。对比 AI 标注，情感一致率达 87%。针对 AI 在“混合情感”上的误判，修订 Prompt 后重跑。
4. **差评痛点洞察**：在 116 条差评中，**排队 (queue)** 与 **游乐设施 (rides)** 是核心痛点（分别占差评的 49.1% 与 48.3%）。

## 📊 Tableau 在线看板
👉 [点击此处查看交互式数据看板](https://public.tableau.com/app/profile/yy.z1700/viz/Disneyland_Review_Analysis_Zhang/1?publish=yes)# Disneyland-Review-Analysis
