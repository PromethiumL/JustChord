#!/usr/bin/env python
"""Check config.jsonc coverage against source code.

Reports:
  1. JSONC keys that are never read by any from_config() or config.get()
  2. config.get() calls in source that reference keys missing from JSONC
  3. Summary of coverage per section
"""

import ast
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "data" / "config.jsonc"
SOURCE_DIRS = [PROJECT_ROOT / "JustChord"]


def load_jsonc_keys():
    """Load all (section, key) pairs from config.jsonc."""
    with open(CONFIG_PATH) as f:
        stripped = "\n".join(line.split("//")[0] for line in f)
    data = json.loads(stripped)
    keys = set()
    for section, values in data.items():
        if isinstance(values, dict):
            for key in values:
                keys.add((section, key))
    return keys


def find_config_reads_in_source():
    """Find all config keys read in Python source via config.get(), config.section(), or from_config()."""
    reads = set()
    source_files = []
    for src_dir in SOURCE_DIRS:
        source_files.extend(src_dir.rglob("*.py"))

    for path in source_files:
        content = path.read_text()

        # Pattern 1: config.get("section", "key", ...)
        for m in re.finditer(r'config\.get\(\s*["\'](\w+)["\']\s*,\s*["\'](\w+)["\']', content):
            reads.add((m.group(1), m.group(2)))

        # Pattern 2: config.section("name") followed by .get("key", ...) calls
        # Find section variable assignments: `xxx = config.section("name")`
        section_vars = {}
        for m in re.finditer(r'(\w+)\s*=\s*config\.section\(\s*["\'](\w+)["\']\s*\)', content):
            section_vars[m.group(1)] = m.group(2)

        # Find .get("key") calls on those variables
        for var_name, section_name in section_vars.items():
            pattern = rf'{re.escape(var_name)}\.get\(\s*["\'](\w+)["\']'
            for m in re.finditer(pattern, content):
                reads.add((section_name, m.group(1)))

        # Pattern 3: kb.get("key"), core.get("key") etc. in from_config methods
        # Try to resolve local vars assigned from config.section()
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            # Track local section vars within functions
            local_sections = {}
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                    target = stmt.targets[0]
                    if isinstance(target, ast.Name) and isinstance(stmt.value, ast.Call):
                        call = stmt.value
                        if (
                            isinstance(call.func, ast.Attribute)
                            and call.func.attr == "section"
                            and call.args
                            and isinstance(call.args[0], ast.Constant)
                        ):
                            local_sections[target.id] = call.args[0].value

            # Also track local helper functions that wrap section_var.get()
            # e.g. `def color(key, default): return tuple(kb.get(key, ...))`
            helper_sections = {}  # func_name -> section_name
            for stmt in ast.walk(node):
                if isinstance(stmt, (ast.FunctionDef, ast.Assign)):
                    # Inline def or lambda: look for var.get(param, ...) patterns
                    inner_func = None
                    if isinstance(stmt, ast.FunctionDef) and stmt.args.args:
                        inner_func = stmt
                    elif (
                        isinstance(stmt, ast.Assign)
                        and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Name)
                        and isinstance(stmt.value, ast.Lambda)
                    ):
                        inner_func = stmt.value
                    if inner_func is None:
                        continue
                    for inner_call in ast.walk(inner_func):
                        if (
                            isinstance(inner_call, ast.Call)
                            and isinstance(inner_call.func, ast.Attribute)
                            and inner_call.func.attr == "get"
                            and isinstance(inner_call.func.value, ast.Name)
                            and inner_call.func.value.id in local_sections
                        ):
                            fname = stmt.name if isinstance(stmt, ast.FunctionDef) else stmt.targets[0].id
                            helper_sections[fname] = local_sections[inner_call.func.value.id]

            # Now find all .get("key") calls on section vars and helper funcs
            for stmt in ast.walk(node):
                if not isinstance(stmt, ast.Call):
                    continue
                # Direct: section_var.get("key", ...)
                if (
                    isinstance(stmt.func, ast.Attribute)
                    and stmt.func.attr == "get"
                    and isinstance(stmt.func.value, ast.Name)
                    and stmt.func.value.id in local_sections
                    and stmt.args
                    and isinstance(stmt.args[0], ast.Constant)
                ):
                    reads.add((local_sections[stmt.func.value.id], stmt.args[0].value))
                # Indirect: helper_func("key", ...)
                if (
                    isinstance(stmt.func, ast.Name)
                    and stmt.func.id in helper_sections
                    and stmt.args
                    and isinstance(stmt.args[0], ast.Constant)
                ):
                    reads.add((helper_sections[stmt.func.id], stmt.args[0].value))

    return reads


def main():
    jsonc_keys = load_jsonc_keys()
    source_reads = find_config_reads_in_source()

    unused = jsonc_keys - source_reads
    missing = source_reads - jsonc_keys

    # Group by section
    sections = sorted(set(s for s, _ in jsonc_keys | source_reads))

    print("=" * 60)
    print("CONFIG COVERAGE REPORT")
    print("=" * 60)

    has_issues = False

    if unused:
        has_issues = True
        print("\n[UNUSED] JSONC keys not read by any source code:")
        for section in sections:
            section_unused = sorted(k for s, k in unused if s == section)
            if section_unused:
                for key in section_unused:
                    print(f"  {section}.{key}")

    if missing:
        has_issues = True
        print("\n[MISSING] Source reads keys absent from JSONC:")
        for section in sections:
            section_missing = sorted(k for s, k in missing if s == section)
            if section_missing:
                for key in section_missing:
                    print(f"  {section}.{key}")

    print(f"\nSummary:")
    print(f"  JSONC keys:     {len(jsonc_keys)}")
    print(f"  Source reads:   {len(source_reads)}")
    print(f"  Matched:        {len(jsonc_keys & source_reads)}")
    print(f"  Unused in JSONC:{len(unused)}")
    print(f"  Missing in JSONC:{len(missing)}")

    if not has_issues:
        print("\n  All config keys are covered.")

    return 1 if has_issues else 0


if __name__ == "__main__":
    sys.exit(main())
