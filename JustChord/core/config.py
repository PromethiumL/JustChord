"""Loads user configuration from data/config.jsonc.

The JSONC file is the single source of defaults. Each config dataclass
defines the schema (field names + types); this module fills values from
the JSONC, falling back to the dataclass default when a key is absent.

Usage in a dataclass module:
    from JustChord.core.config import from_section

    @dataclass
    class MyConfig:
        some_flag: bool = True
        size: int = 10

    cfg = from_section(MyConfig, "my_section")
"""

import dataclasses
import json
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "config.jsonc"
_config: dict = {}


def _load():
    global _config
    if not _CONFIG_PATH.exists():
        _config = {}
        return
    with open(_CONFIG_PATH) as f:
        stripped = "\n".join(line.split("//")[0] for line in f)
    _config = json.loads(stripped)


def get(section_name, key, default=None):
    """Read a config value. Returns default if section or key is missing."""
    return _config.get(section_name, {}).get(key, default)


def section(name):
    """Return an entire config section as a dict, or empty dict if missing."""
    return dict(_config.get(name, {}))


def from_section(dataclass_type, section_name):
    """Create a dataclass instance with values merged from a JSONC section.

    Keys in the JSONC section that match dataclass field names override
    the dataclass defaults. Tuple-typed fields (e.g. colors) are converted
    from JSON arrays automatically. Unknown keys in the JSONC are ignored.
    """
    sec = _config.get(section_name, {})
    fields = {f.name: f for f in dataclasses.fields(dataclass_type)}
    kwargs = {}
    for name, field in fields.items():
        if name not in sec:
            continue
        val = sec[name]
        # JSON arrays → tuples for color fields etc.
        if isinstance(val, list) and field.type in ("Tuple[int, int, int]", tuple):
            val = tuple(val)
        kwargs[name] = val
    return dataclass_type(**kwargs)


def reload():
    """Reload config from disk."""
    _load()


# Load on import
_load()
