from . import config

def get_key(backend):
    conf = config.Config()
    conf.load()
    return conf.backend_keys.get(backend)
