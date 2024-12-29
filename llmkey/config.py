
import contextlib
import json
from pathlib import Path
from typing import Callable, Concatenate
from typing import Optional as O
from typing import ParamSpec, TypeVar

import appdirs

class ConfigIO:
    @contextlib.contextmanager
    def with_data(self):
        self.ensure_dir()
        if self.config_file().exists():
            with open(self.config_file()) as f:
                data = json.load(f)
                yield data
        else:
            yield None

    def save_data(self, data):
        self.ensure_dir()
        with open(self.config_file(), "w") as f:
            json.dump(data, f)

    @staticmethod
    def dir():
        return Path(appdirs.user_config_dir()) / "llmkey"

    def ensure_dir(self):
        self.dir().mkdir(exist_ok=True)

    def config_file(self):
        return self.dir() / "config.json"


class ConfigDictIO:
    def __init__(self, dict_store):
        self.dict_store = dict_store

    @contextlib.contextmanager
    def with_data(self):
        if self.dict_store:
            yield self.dict_store
        else:
            yield None

    def save_data(self, data):
        del data
        pass


class Config:
    model:str

    def __init__(self):
        self.io = ConfigIO()
        self.model: O[str] = None
        self.backend: O[str] = None
        self.backend_models: O[dict[str, str]] = {}
        self.backend_keys: O[dict[str, str]] = {}
        self.first_run: O[bool] = True
        self.configIO = ConfigIO()


    def load(self):
        with self.io.with_data() as data:
            if data is not None:
                self.model = data["model"]
                self.backend = data["backend"]
                self.backend_models = data["backend_models"]
                self.backend_keys = data["backend_keys"]
                self.first_run = data["first_run"]


    def save(self):
        data = dict(
            model=self.model,
            backend=self.backend,
            backend_models=self.backend_models,
            backend_keys=self.backend_keys,
            first_run=self.first_run,)
        self.io.save_data(data)


def mock_config(store_dict: dict):
    config = Config()
    config.io = ConfigDictIO(store_dict)
    return config



P, T = ParamSpec('P'), TypeVar('T')
def with_config(f: Callable[P, T]) -> Callable[Concatenate[Config, P], T]:
    config = Config()
    config.load()
    def inner(*args, **kwargs):
        return f(config, *args, **kwargs)
    config.save()
    return inner
