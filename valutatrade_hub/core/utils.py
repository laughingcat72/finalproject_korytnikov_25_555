import json
from pathlib import Path


class FileManager:

    def __init__(self, base_dir="data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def _get_file_path(self, filename: str):
        return self.base_dir / filename

    def read_json(self, filename: str, default=[]):
        file_path = self._get_file_path(filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return default

    def write_json(self, filename: str, data: dict):
        file_path = self._get_file_path(filename)
        file_json = self.read_json(filename, [])
        file_json.append(data)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(file_json, f, indent=2, ensure_ascii=False)
        return True

    def update_json(self, filename: str, data: list):
        file_path = self._get_file_path(filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
