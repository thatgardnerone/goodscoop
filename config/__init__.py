import os
from typing import Self

class Config:
    _instance = None

    def __new__(cls):
        cls._instance = super(Config, cls).__new__(cls)
        cls.config_dict = {}
        cls.load_config()

        return cls._instance

    @staticmethod
    def load_config():
        """
        Auto-discover config files
        """
        config_dir = os.path.dirname(__file__)

        for filename in os.listdir(config_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                module = __import__(f'config.{module_name}', fromlist=['config'])
                Config._instance.config_dict[module_name] = module.config

    @staticmethod
    def get(path, default=None):
        config_instance = Config()

        keys = path.split('.')

        # Start with the base configuration dictionary
        current_level = config_instance.config_dict

        # Traverse the dictionary to get the value
        for key in keys[:-1]:
            if key not in current_level or not isinstance(current_level[key], dict):
                return default

            current_level = current_level[key]

        final_key = keys[-1]

        return current_level.get(final_key, default)

    def reload(self):
        self._instance = None
        Config()

def config(path, default=None):
    """
    A simple helper function that wraps `Config.get`
    :return:
    """
    return Config.get(path, default)
