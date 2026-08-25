# 路径规划虚拟仿真闭环 AI 科学家系统

本仓库的唯一开发主线是 [`路径规划虚拟仿真闭环AI科学家系统/`](路径规划虚拟仿真闭环AI科学家系统/)。
近期目标是完成可复现、可解释、可演示的 **2D 栅格地图比赛版闭环**。

## 当前主链路

地图/参数输入 → 环境分析 → 文献与历史实验检索 → 五算法统一实验 →
数据驱动选型与参数推荐 → 科学假设 → 实验验证 → 反思 → 人工复核 → 报告。

算法白名单：A*、ACO、PSO、SA、混合优化算法。

## 本地验证

```powershell
cd ".\路径规划虚拟仿真闭环AI科学家系统"
.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider tests -q
.\.venv\Scripts\python.exe -B .\main.py
```

真实密钥只允许保存在本地 `.env` 或 Streamlit secrets 中，不得提交到 Git。

详细资产分类见 [`docs/PROJECT_INVENTORY.md`](docs/PROJECT_INVENTORY.md)，近期路线见
[`docs/ROADMAP_2D_GRID_COMPETITION.md`](docs/ROADMAP_2D_GRID_COMPETITION.md)。大型地图、文献和
二进制报告存放在本地 `assets/`；可复核的小型实验结果位于 `evidence/`。
完整的本地资产位置与恢复校验见 [`docs/ASSET_MANIFEST.md`](docs/ASSET_MANIFEST.md)。
