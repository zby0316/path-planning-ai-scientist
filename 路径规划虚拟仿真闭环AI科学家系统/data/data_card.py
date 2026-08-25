"""DataCardGenerator：自动为数据集生成标准化的 10 字段数据卡（data_card.md）。"""
from pathlib import Path

from data.data_manager import DataManager


class DataCardGenerator:
    """数据集说明卡生成器：按 10 行固定结构写出 Markdown 格式的数据卡。"""

    def __init__(self, data_manager=None):
        self.data_manager = data_manager or DataManager()

    def generate(
        self,
        dataset_name,
        source,
        download_url,
        license_info,
        map_type,
        map_count,
        task_count,
        purpose,
        preprocessing,
        reproducible,
        output_dir=None,
    ) -> Path:
        """按 10 行固定结构生成数据卡，写入 output_dir / "data_card.md"，返回写入路径。"""
        output_dir = Path(output_dir) if output_dir else self.data_manager.get_path("movingai_2d")
        DataManager.ensure_dir(output_dir)

        content = (
            f"# 数据卡：{dataset_name}\n"
            f"- **数据集名称**：{dataset_name}\n"
            f"- **来源**：{source}\n"
            f"- **下载链接**：{download_url}\n"
            f"- **许可协议**：{license_info}\n"
            f"- **地图类型**：{map_type}\n"
            f"- **地图数量**：{map_count}\n"
            f"- **起终点任务数量**：{task_count}\n"
            f"- **使用目的**：{purpose}\n"
            f"- **预处理方式**：{preprocessing}\n"
            f"- **是否可复现**：{reproducible}\n"
        )

        target = output_dir / "data_card.md"
        target.write_text(content, encoding="utf-8")
        return target

    def generate_from_movingai(self, map_name: str, map_count: int = 1, task_count: int = 0) -> Path:
        """为 Moving AI 2D 数据集自动填充字段并生成数据卡。"""
        dataset_name = f"Moving AI 2D - {map_name}"
        source = "https://www.movingai.com/benchmarks/grids.html"
        download_url = f"https://www.movingai.com/benchmarks/grids/{map_name}.map"
        license_info = "学术使用"
        map_type = "2D 栅格地图"
        purpose = "作为路径规划算法适配实验的公开基准地图"
        preprocessing = "无预处理；如需可统一做障碍二值化（@/O/T/W→1，.→0）"
        reproducible = True

        return self.generate(
            dataset_name=dataset_name,
            source=source,
            download_url=download_url,
            license_info=license_info,
            map_type=map_type,
            map_count=map_count,
            task_count=task_count,
            purpose=purpose,
            preprocessing=preprocessing,
            reproducible=reproducible,
            output_dir=self.data_manager.get_path("movingai_2d"),
        )
