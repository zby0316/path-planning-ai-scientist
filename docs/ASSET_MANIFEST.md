# 本地资产清单

生成日期：2026-08-25  
管理原则：本文件进入 Git；下列资产目录仅保留在本地，不进入普通 Git。

| 位置 | 内容 | 文件数 | 大小 | 目录清单 SHA-256 |
|---|---|---:|---:|---|
| `assets/maps/` | 2D 栅格地图（城市/街道与 Warcraft 地图） | 126 | 48.50 MB | `df378506cced24f31ce3a71a8b57f00ba7141fd66e0aa4768da38490a8a9e477` |
| `assets/literature/` | 路径规划 PDF、CAJ 与 Markdown 原文 | 92 | 207.62 MB | `4c56f71086a65628b12b783e2d59b1ad4c244104eec5183c69d261908081b51b` |
| `assets/reports/` | DOCX/PDF 成品、图表与最终视觉 QA | 82 | 38.71 MB | `61ae736c5ac88d960e98447156d7328c345ffe29e210259bcf03858653539707` |
| `archive/legacy_backup/` | 历史代码快照，不作为当前主线 | 218 | 6.78 MB | `8634736ac9f464a78c2c2a77b40bcaa57c8bccbf9fa56b9b55449d0a3abbf6cf` |
| `archive/legacy_trae/` | 根级历史 Trae 规格 | 9 | 0.06 MB | `8bfbcba960e713e29303cc91b64d158feeeda437afc224ac712416c6aaea6004` |

## 跟踪边界

- `evidence/validated_experiments/` 的 8 个小型 CSV、JSON、NPZ、XLSX 结果进入 Git，作为比赛报告的可复核证据。
- `assets/` 与 `archive/legacy_backup/` 被 `.gitignore` 排除；更换电脑时须从本地备份复制回相同位置，或通过 `ASSETS_DIR` 指向外部资产盘。
- 文献导入工具默认读取 `assets/literature/sources/`，且默认仅预览；只有显式 `--write` 才会更新主线文献知识库。

## 校验方法

迁移、备份恢复或外部硬盘挂载后，应分别计算每个目录内按相对路径排序的
`相对路径 | 文件 SHA-256` 清单哈希，并与上表比较。文件数、总大小或清单哈希不一致时，不应删除原位置副本。
