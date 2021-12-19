# coding: utf-8
from configs import defaults
from configs import config


class Settings(object):
    def __init__(self):
        self.configs = {}
        attrs = dir(defaults)
        for attr in [att for att in attrs if not att.startswith("__")]:
            self.configs[attr] = getattr(defaults, attr)
        attrs = dir(config)
        for attr in [att for att in attrs if not att.startswith("__")]:
            self.configs[attr] = getattr(config, attr)

    def __getattr__(self, item):
        return self.configs[item]

    def __repr__(self):
        return "\n".join([f"{k}: {v}" for k, v in self.configs.items()])


settings = Settings()
