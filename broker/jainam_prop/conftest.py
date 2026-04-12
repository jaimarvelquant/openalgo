import sys
from importlib import util
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
root_str = str(project_root)

if root_str not in sys.path:
    sys.path.insert(0, root_str)

package_path = str(Path(__file__).resolve().parent)
if package_path in sys.path:
    sys.path.remove(package_path)

database_init = project_root / 'database' / '__init__.py'


def _load_real_database_module():
    if not database_init.exists():
        return

    spec = util.spec_from_file_location(
        'database',
        database_init,
        submodule_search_locations=[str(project_root / 'database')],
    )
    if not spec or not spec.loader:
        return

    database_module = util.module_from_spec(spec)
    spec.loader.exec_module(database_module)
    sys.modules['database'] = database_module


def _database_is_mock():
    module = sys.modules.get('database')
    file_attr = getattr(module, '__file__', None) if module is not None else None
    return module is None or not isinstance(file_attr, str)


if _database_is_mock():
    _load_real_database_module()


def pytest_runtest_setup(item):  # noqa: ARG001
    if _database_is_mock():
        _load_real_database_module()
