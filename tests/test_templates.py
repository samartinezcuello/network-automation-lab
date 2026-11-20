#!/usr/bin/env python3
"""Render the Jinja2 templates for each leaf and compare the result with the golden
configuration captured from the working lab (tests/golden/<leaf>.json).

No Ansible and no running lab are needed: it only checks that the data model plus the
templates still produce the configuration that is known to work.
"""

import json
import sys
from pathlib import Path

import jinja2
import yaml

ROOT = Path(__file__).resolve().parent.parent

# Same order as the paths captured by playbooks/01-capture.yml
CAPTURED_PATHS = [
    "/interface[name=ethernet-1/1]",
    "/interface[name=ethernet-1/2]",
    "/interface[name=system0]",
    "/tunnel-interface[name=vxlan1]",
    "/network-instance[name=default]/protocols/bgp",
    "/network-instance[name=mac-vrf-1]",
    "/routing-policy",
]


def canonical(obj):
    """Sort dict keys and list items so the comparison ignores ordering."""
    if isinstance(obj, dict):
        return {key: canonical(value) for key, value in sorted(obj.items())}
    if isinstance(obj, list):
        return sorted((canonical(item) for item in obj), key=lambda item: json.dumps(item, sort_keys=True))
    return obj


def render(leaf):
    """Render every template for one leaf and return {path: value}."""
    variables = {}
    for name in (ROOT / "inventory/group_vars/all.yml", ROOT / "inventory/host_vars" / f"{leaf}.yml"):
        variables.update(yaml.safe_load(name.read_text()))
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    updates = []
    for template in sorted((ROOT / "templates/srlinux").glob("*.j2")):
        updates += yaml.safe_load(env.from_string(template.read_text()).render(**variables))
    return {update["path"]: update["value"] for update in updates}


def main():
    failures = 0
    for golden_file in sorted((ROOT / "tests/golden").glob("*.json")):
        leaf = golden_file.stem
        golden = json.loads(golden_file.read_text())
        rendered = render(leaf)
        for path, expected in zip(CAPTURED_PATHS, golden):
            if canonical(rendered.get(path)) == canonical(expected):
                print(f"PASS {leaf} {path}")
            else:
                failures += 1
                print(f"FAIL {leaf} {path}")
                print("  rendered:", json.dumps(canonical(rendered.get(path)))[:400])
                print("  golden:  ", json.dumps(canonical(expected))[:400])
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())