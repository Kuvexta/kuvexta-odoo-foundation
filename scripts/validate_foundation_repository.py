#!/usr/bin/env python3
"""Validate Foundation boundaries, physical state and migration receipts."""

from __future__ import annotations

import ast
import json
import logging
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "MIGRATION_MANIFEST.json"
LOGGER = logging.getLogger(__name__)
IGNORED_DIRS = {".git", ".github", "scripts"}
PHYSICAL_STATE = "physically_migrated_without_relicense"
EXPECTED_LICENSE = "LGPL-3"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def git_tree(module: str) -> str | None:
    """Return the checked-out Git subtree SHA when repository metadata is available."""
    if not (ROOT / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", f"HEAD:{module}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def validate_receipt(
    module: str,
    manifest: dict,
    receipt_path: Path,
    expected_source: str,
    errors: list[str],
) -> None:
    receipt = load_json(receipt_path)
    if receipt.get("module") != module:
        errors.append(f"{module}: receipt module mismatch")
    if receipt.get("source_repository") != expected_source:
        errors.append(f"{module}: receipt source_repository mismatch")
    if receipt.get("exact_tree_match") is not True:
        errors.append(f"{module}: receipt must assert exact_tree_match=true")

    source_tree = receipt.get("source_tree_sha")
    target_tree = receipt.get("target_tree_sha")
    if not source_tree or source_tree != target_tree:
        errors.append(f"{module}: receipt source_tree_sha and target_tree_sha must match")
    actual_tree = git_tree(module)
    if actual_tree is not None and target_tree != actual_tree:
        errors.append(
            f"{module}: receipt target_tree_sha {target_tree!r} != checked-out tree {actual_tree!r}"
        )

    manifest_license = manifest.get("license")
    receipt_license = receipt.get("effective_license") or receipt.get("license_preserved")
    if receipt_license != manifest_license:
        errors.append(
            f"{module}: receipt license {receipt_license!r} != manifest license {manifest_license!r}"
        )
    if receipt.get("source_deleted") is not False:
        errors.append(f"{module}: initial migration receipt must keep source_deleted=false")
    if receipt.get("relicensing") is True:
        errors.append(f"{module}: physical migration receipt cannot assert relicensing=true")
    if receipt.get("schema_version", 1) >= 2 and receipt.get("relicensing") is not False:
        errors.append(f"{module}: receipt schema >=2 must explicitly set relicensing=false")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    policy = load_json(MANIFEST_PATH)
    planned_states = policy.get("planned_modules", {})
    planned = set(planned_states)
    declared_physical = set(policy.get("physical_modules", []))
    receipts = policy.get("migration_receipts", {})
    addons = discover_addons()
    actual_physical = set(addons)
    errors: list[str] = []

    if policy.get("schema_version") != 4:
        errors.append("Foundation MIGRATION_MANIFEST schema_version must be 4")
    if policy.get("repository_role") != "foundation":
        errors.append("Foundation repository_role must remain 'foundation'")
    rules = policy.get("rules", {})
    for key in (
        "may_depend_on_professional",
        "may_depend_on_community_agpl",
        "may_depend_on_vendor_adapters",
        "may_depend_on_internal",
        "optional_cross_repository_dependencies_allowed",
    ):
        if rules.get(key) is not False:
            errors.append(f"Foundation rule {key!r} must remain false")
    if rules.get("license_change_during_migration_allowed") is not False:
        errors.append("Foundation physical migration must not change license")

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
    if set(receipts) != declared_physical:
        errors.append("migration_receipts keys must exactly match physical_modules")

    for module, manifest in sorted(addons.items()):
        if planned_states.get(module) != PHYSICAL_STATE:
            errors.append(
                f"{module}: physical addon state {planned_states.get(module)!r}; expected {PHYSICAL_STATE!r}"
            )
        if manifest.get("license") != EXPECTED_LICENSE:
            errors.append(
                f"{module}: Foundation requires preserved {EXPECTED_LICENSE}; found {manifest.get('license')!r}"
            )
        receipt_rel = receipts.get(module)
        if not receipt_rel:
            errors.append(f"{module}: physical migration requires a receipt entry")
        else:
            receipt_path = ROOT / receipt_rel
            if not receipt_path.is_file():
                errors.append(f"{module}: migration receipt does not exist: {receipt_rel}")
            else:
                validate_receipt(
                    module,
                    manifest,
                    receipt_path,
                    policy.get("source_repository"),
                    errors,
                )
        for dependency in manifest.get("depends", []):
            if dependency.startswith("kt_") and dependency not in actual_physical:
                errors.append(
                    f"{module}: Kuvexta dependency {dependency!r} crosses Foundation boundary"
                )

    for module, state in sorted(planned_states.items()):
        if state == PHYSICAL_STATE and module not in actual_physical:
            errors.append(f"{module}: marked physically migrated but addon is absent")

    if errors:
        for error in errors:
            LOGGER.error(error)
        return 1
    LOGGER.info(
        "Foundation boundary valid: %d physical addons; manifests, receipts, Git trees and licenses agree.",
        len(addons),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
