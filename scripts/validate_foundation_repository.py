#!/usr/bin/env python3
"""Validate Kuvexta Foundation repository boundaries and migration-state drift."""

from __future__ import annotations

import ast
import json
import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "MIGRATION_MANIFEST.json"
LOGGER = logging.getLogger(__name__)

IGNORED_DIRS = {".git", ".github", "scripts"}
PHYSICAL_STATE = "physically_migrated_without_relicense"


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
    planned_states = policy.get("planned_modules", {})
    planned = set(planned_states)
    declared_physical = set(policy.get("physical_modules", []))
    receipts = policy.get("migration_receipts", {})
    addons = discover_addons()
    actual_physical = set(addons)
    errors: list[str] = []

    unexpected = sorted(actual_physical - planned)
    if unexpected:
        errors.append("Unexpected addons in Foundation: " + ", ".join(unexpected))

    if declared_physical != actual_physical:
        missing = sorted(actual_physical - declared_physical)
        stale = sorted(declared_physical - actual_physical)
        if missing:
            errors.append("physical_modules missing present addons: " + ", ".join(missing))
        if stale:
            errors.append("physical_modules declares absent addons: " + ", ".join(stale))

    for module, manifest in sorted(addons.items()):
        if planned_states.get(module) != PHYSICAL_STATE:
            errors.append(
                f"{module}: addon is physically present but planned_modules state is "
                f"{planned_states.get(module)!r}, expected {PHYSICAL_STATE!r}"
            )
        receipt = receipts.get(module)
        if not receipt:
            errors.append(f"{module}: physical migration requires a receipt entry")
        elif not (ROOT / receipt).is_file():
            errors.append(f"{module}: migration receipt does not exist: {receipt}")

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

    for module, state in sorted(planned_states.items()):
        if state == PHYSICAL_STATE and module not in actual_physical:
            errors.append(f"{module}: marked physically migrated but addon is absent")

    camera_state = planned_states.get("kt_camera_scan_widget")
    if "kt_camera_scan_widget" in addons and camera_state != PHYSICAL_STATE:
        errors.append(
            "kt_camera_scan_widget is physically present without completed migration state"
        )

    if errors:
        for error in errors:
            LOGGER.error(error)
        return 1

    LOGGER.info(
        "Foundation boundary valid: %d physical addon(s), manifest and receipts synchronized.",
        len(addons),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
