import typing as t
from importlib.metadata import entry_points


def discover_plugins() -> t.Generator[dict[str, t.Any], None, None]:
    """
    Discover plugins using the 'aiidalab_qe.plugins' entry point group.
    Each plugin must define a callable that returns a dict with keys: id, label, schemas.
    """
    eps = entry_points(group="aiidalab_qe.plugins")
    for ep in eps:
        plugin = ep.load()()
        yield plugin
