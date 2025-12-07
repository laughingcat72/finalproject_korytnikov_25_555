import json
from pathlib import Path
from .settings import SettingsLoader


class DatabaseManager:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.settings = SettingsLoader()
            self._initialized = True

    def _get_file_path(self, filename: str) -> Path:
        data_dir = self.settings.get("data_directory")
        if not data_dir:
            data_dir = "data/"
        return Path(data_dir) / filename

    def read_json(self, filename: str, default=None):
        file_path = self._get_file_path(filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return default if default is not None else []
        except Exception as e:
            print(f"Ошибка чтения {filename}: {e}")
            return default if default is not None else []

    def write_json(self, filename: str, data):
        file_path = self._get_file_path(filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка записи {filename}: {e}")
            return False

    def update_json(self, filename: str, data):
        return self.write_json(filename, data)
