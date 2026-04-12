"""Utility helpers to guarantee the real database package is available."""

from __future__ import annotations

import sys
from importlib import util
from pathlib import Path
from types import ModuleType


_MODULE_MAP = {
    "database": ("database", True),
    "utils": ("utils", True),
    "utils.logging": ("utils/logging.py", False),
    "utils.httpx_client": ("utils/httpx_client.py", False),
    "broker.jainam_prop.mapping": ("broker/jainam_prop/mapping", True),
    "broker.jainam_prop.database": ("broker/jainam_prop/database", True),
}


def _ensure_module(name: str, relative_path: str, is_package: bool) -> None:
    module = sys.modules.get(name)
    file_attr = getattr(module, "__file__", None) if module is not None else None
    if isinstance(file_attr, str):  # already real module
        return

    project_root = Path(__file__).resolve().parents[2]
    target_path = project_root / relative_path

    if is_package:
        init_path = target_path / "__init__.py"
        if not init_path.exists():
            return
        spec = util.spec_from_file_location(
            name,
            init_path,
            submodule_search_locations=[str(target_path)],
        )
    else:
        if not target_path.exists():
            return
        spec = util.spec_from_file_location(name, target_path)

    if not spec or not spec.loader:  # pragma: no cover
        return

    module_obj = util.module_from_spec(spec)
    spec.loader.exec_module(module_obj)
    sys.modules[name] = module_obj


def ensure_core_modules():
    for name, (path, is_package) in _MODULE_MAP.items():
        _ensure_module(name, path, is_package)


def ensure_database_package():
    ensure_core_modules()
