# Plugin architecture for taggers, centrality, scorers, selectors
from importlib import import_module

def load_class(path: str):
    # e.g., "pkg.module:ClassName"
    if ":" not in path:
        raise ValueError(f"Invalid plugin path '{path}'. Expected 'module:Class'")
    mod, cls = path.split(":", 1)
    module = import_module(mod)
    return getattr(module, cls)
