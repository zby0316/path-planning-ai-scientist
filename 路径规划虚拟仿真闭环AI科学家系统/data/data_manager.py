"""DataManager：统一管理 data/ 下各类数据目录的创建、查询与枚举。"""
from pathlib import Path

from config import DATA_DIR


class DataManager:
    _CATEGORY_PATHS = {
        "movingai_2d": "raw/movingai_2d",
        "movingai_3d": "raw/movingai_3d",
        "osm": "raw/osm",
        "uploaded": "raw/uploaded",
        "grid_maps": "processed/grid_maps",
        "topology_graphs": "processed/topology_graphs",
        "dynamic_maps": "processed/dynamic_maps",
        "experiments": "experiments",
        "raw_pdf": "literature/raw_pdf",
        "metadata": "literature/metadata",
        "extracted_facts": "literature/extracted_facts",
        "references": "literature/references",
    }

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root is not None else Path(DATA_DIR)
        self._categories = dict(self._CATEGORY_PATHS)
        for rel in self._categories.values():
            (self.root / rel).mkdir(parents=True, exist_ok=True)

    def get_path(self, category: str) -> Path:
        if category not in self._categories:
            raise ValueError(f"未知的数据类别: {category}")
        return self.root / self._categories[category]

    def list_files(self, category: str, pattern: str = "*") -> list[Path]:
        base = self.get_path(category)
        return [p for p in base.glob(pattern) if p.is_file()]

    @staticmethod
    def ensure_dir(path) -> Path:
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p
