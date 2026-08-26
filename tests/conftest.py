"""Load each analysis's modules by path.

Every analysis owns a `data.py`, a `figures.py` and a `pipeline.py`. Putting all
the analysis folders on `sys.path` makes those names collide and whichever
folder sorts first silently wins -- so modules are loaded explicitly instead,
registered under a namespaced key.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYSES = ROOT / "analyses"


def load(analysis: str, module: str):
    """Import `analyses/<analysis>/<module>.py` under a unique name."""
    key = f"{analysis}.{module}"
    if key in sys.modules:
        return sys.modules[key]
    folder = ANALYSES / analysis
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
    spec = importlib.util.spec_from_file_location(key, folder / f"{module}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod
