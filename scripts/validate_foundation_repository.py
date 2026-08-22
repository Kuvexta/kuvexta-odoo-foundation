#!/usr/bin/env python3
"""Validate Kuvexta Foundation repository boundaries.

The validator is intentionally stdlib-only. It checks the migration manifest and,
when Odoo addons are present at repository root, verifies that only planned
Foundation modules are present, that their manifest license stays LGPL-3 during
migration, and that no internal dependency points to a module outside Foundation.
"""

from __future__ import annotations

import ast
import json
import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "MIGRATION_MANIFEST.json"
LOGGER = logging.getLogger(__name__)

IGNORED_DIRS = {".git", ".github", "scripts"}


def load_policy() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def discover_addons() -> dict[str, dict]:
    addons: dict[str, dict] = {}
    for path in ROOT.iterdir():
        if not path.is_dir() or path.name in IGNORED_DIRS:
            continue
        manifest = path / "__manifest__.py"
        if not manifest.exists():
            continue
        try:
            value = ast.literal_eval(manifest.read_text(encoding="utf-8"))
        except (SyntaxError, ValueError) as exc:
            raise ValueError(f"Invalid Odoo manifest: {manifest}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Odoo manifest must be a dict: {manifest}")
        addons[path.name] = value
    return addons


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    policy = load_policy()
    planned = set(policy.get("planned_modules", {}))
    addons = discover_addons()
    errors: list[str] = []

    unexpected = sorted(set(addons) - planned)
    if unexpected:
        errors.append("Unexpected addons in Foundation: " + ", ".join(unexpected))

    for module, manifest in sorted(addons.items()):
        license_name = manifest.get("license")
        if license_name != "LGPL-3":
            errors.append(
                f"{module}: migration must preserve Foundation license LGPL-3; "
                f"found {license_name!r}"
            )

        for dependency in manifest.get("depends", []):
            if dependency.startswith("kt_") and dependency not in planned:
                errors.append(
                    f"{module}: internal Kuvexta dependency {dependency!r} is not "
                    "planned in Foundation"
                )

    camera_state = policy.get("planned_modules", {}).get("kt_camera_scan_widget")
    if "kt_camera_scan_widget" in addons and camera_state == "blocked_third_party_notices":
        errors.append(
            "kt_camera_scan_widget is physically present while its third-party notices "
            "gate is still blocked"
        )

    if errors:
        for error in errors:
            LOGGER.error(error)
        return 1

    LOGGER.info(
        "Foundation boundary valid: %d addon(s) present, %d planned.",
        len(addons),
        len(planned),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
