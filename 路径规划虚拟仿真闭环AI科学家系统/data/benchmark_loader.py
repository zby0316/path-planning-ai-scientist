"""BenchmarkLoader：从 Moving AI 公开站点按需下载栅格基准地图与场景。"""
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from data.data_manager import DataManager
from map.map_parser import MapParser


class BenchmarkLoader:
    """Moving AI 2D 栅格基准下载与解析入口。"""

    BASE_URL = "https://www.movingai.com/benchmarks/grids/"
    AVAILABLE_MAPS = [
        "dao/arena",
        "dao/arena2",
        "dao/brc000d",
        "dao/brc300d",
        "dao/brc600d",
        "dao/den000d",
        "dao/den300d",
        "dao/den600d",
        "dao/den900d",
    ]

    def __init__(self, data_manager=None):
        """初始化下载器：解析目标目录、初始化日志文件。"""
        self.data_manager = data_manager or DataManager()
        self.target_dir = self.data_manager.get_path("movingai_2d")
        self.log_path = self.target_dir / "download_log.json"
        if not self.log_path.exists():
            self._write_log([])

    def list_available_maps(self) -> list[str]:
        """返回推荐的 9 个 dao 系列地图集名称的副本。"""
        return list(self.AVAILABLE_MAPS)

    def _write_log(self, records: list) -> None:
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def _append_log(self, entry: dict) -> None:
        if self.log_path.exists():
            with open(self.log_path, "r", encoding="utf-8") as f:
                try:
                    records = json.load(f)
                except json.JSONDecodeError:
                    records = []
        else:
            records = []
        records.append(entry)
        self._write_log(records)

    def _download(self, url: str, dest: Path, timeout: float = 30.0) -> tuple[int, bool]:
        """从 URL 下载内容写入 dest。已存在时跳过；失败包装为 RuntimeError。"""
        if dest.exists():
            return 0, True
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                data = resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            raise RuntimeError(f"下载失败: {url} -> {e}") from e
        with open(dest, "wb") as f:
            f.write(data)
        return len(data), False

    def _record(self, url: str, filename: str, size_bytes: int, skipped: bool) -> None:
        self._append_log(
            {
                "timestamp": datetime.now(timezone.utc)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z"),
                "filename": filename,
                "url": url,
                "size_bytes": size_bytes,
                "skipped": skipped,
            }
        )

    def download_movingai_2d(self, map_name: str) -> dict:
        """下载指定 map_name 对应的 .map 与 .map.scen 文件并落盘。"""
        basename = map_name.split("/")[-1]
        map_url = f"{self.BASE_URL}{map_name}.map"
        scen_url = f"{self.BASE_URL}{map_name}.map.scen"
        map_dest = self.target_dir / f"{basename}.map"
        scen_dest = self.target_dir / f"{basename}.map.scen"

        results: list[dict] = []
        scen_available = True

        try:
            size, skipped = self._download(map_url, map_dest)
            results.append(
                {
                    "url": map_url,
                    "filename": map_dest.name,
                    "size_bytes": size,
                    "skipped": skipped,
                }
            )
            self._record(map_url, map_dest.name, size, skipped)
        except RuntimeError as e:
            raise RuntimeError(f"下载 .map 失败: {map_name} -> {e}") from e

        try:
            size, skipped = self._download(scen_url, scen_dest)
            results.append(
                {
                    "url": scen_url,
                    "filename": scen_dest.name,
                    "size_bytes": size,
                    "skipped": skipped,
                }
            )
            self._record(scen_url, scen_dest.name, size, skipped)
        except RuntimeError as e:
            scen_available = False
            if scen_dest.exists():
                try:
                    scen_dest.unlink()
                except OSError:
                    pass

        return {
            "map_name": map_name,
            "map_file": f"{basename}.map",
            "scen_file": f"{basename}.map.scen" if scen_available else None,
            "scen_available": scen_available,
            "results": results,
        }

    def load_map(self, map_name: str) -> dict:
        """解析指定 map_name 的 .map（必要时自动下载）。"""
        basename = map_name.split("/")[-1]
        map_path = self.target_dir / f"{basename}.map"
        if not map_path.exists():
            self.download_movingai_2d(map_name)
        return MapParser().parse(map_path)
