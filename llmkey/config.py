
import json
from pathlib import Path
from typing import Callable,  Concatenate, ParamSpec, TypeVar

from typing import Optional as O

import appdirs

class Config:
    model:str

    def __init__(self):
        self.model: O[str] = None
        self.backend: O[str] = None
        self.backend_models: O[dict[str, str]] = {}
        self.backend_keys: O[dict[str, str]] = {}
        self.first_run: O[bool] = True

    @staticmethod
    def dir():
        return Path(appdirs.user_config_dir()) / "llmkey"

    def ensure_dir(self):
        self.dir().mkdir(exist_ok=True)

    def config_file(self):
        return self.dir() / "config.json"

    def load(self):
        self.ensure_dir()

        if self.config_file().exists():
            with open(self.config_file()) as f:
                data = json.load(f)
                self.model = data["model"]
                self.backend = data["backend"]
                self.backend_models = data["backend_models"]
                self.backend_keys = data["backend_keys"]
                self.first_run = data["first_run"]

    def save(self):
        self.ensure_dir()
        data = dict(
            model=self.model,
            backend=self.backend,
            backend_models=self.backend_models,
            backend_keys=self.backend_keys,
            first_run=self.first_run,)
        with open(self.config_file(), "w") as f:
            json.dump(data, f)


P, T = ParamSpec('P'), TypeVar('T')
def with_config(f: Callable[P, T]) -> Callable[Concatenate[Config, P], T]:
    config = Config()
    config.load()
    def inner(*args, **kwargs):
        return f(config, *args, **kwargs)
    config.save()
    return inner
