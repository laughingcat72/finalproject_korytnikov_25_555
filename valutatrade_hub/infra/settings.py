class SettingsLoader:

    # Реализация через __new__ выбрана по следующим причинам:
    # 1. ПРОСТОТА - минимальный код, понятный даже начинающим
    # 2. ЧИТАБЕЛЬНОСТЬ - явно видно логику создания единственного экземпляра

    _instance = None

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):

        self._config = {
            "data_directory": "data/",
            "rates_ttl_seconds": 300,
            "default_base_currency": "USD",
            "log_file_path": "logs/valutatrade.log"
        }

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def reload(self):
        """Перезагрузка конфигурации"""
        self._load_config()
