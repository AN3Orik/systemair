from __future__ import annotations

import json
import unittest
from pathlib import Path


MANIFEST_PATH = Path("custom_components/systemair/manifest.json")


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def _pymodbus_requirement() -> str:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return next(requirement for requirement in manifest["requirements"] if requirement.startswith("pymodbus"))


def _allows_version(requirement: str, version: str) -> bool:
    specifiers = requirement.removeprefix("pymodbus").split(",")
    version_tuple = _version_tuple(version)

    for specifier in specifiers:
        specifier = specifier.strip()
        if not specifier:
            continue

        if specifier.startswith("=="):
            if version_tuple != _version_tuple(specifier[2:]):
                return False
            continue

        if specifier.startswith(">="):
            if version_tuple < _version_tuple(specifier[2:]):
                return False
            continue

        if specifier.startswith("<="):
            if version_tuple > _version_tuple(specifier[2:]):
                return False
            continue

        if specifier.startswith(">"):
            if version_tuple <= _version_tuple(specifier[1:]):
                return False
            continue

        if specifier.startswith("<"):
            if version_tuple >= _version_tuple(specifier[1:]):
                return False

    return True


class ManifestRequirementsTest(unittest.TestCase):
    def test_pymodbus_requirement_allows_supported_versions(self) -> None:
        requirement = _pymodbus_requirement()

        self.assertTrue(_allows_version(requirement, "3.11.2"))
        self.assertTrue(_allows_version(requirement, "3.13.1"))

    def test_pymodbus_requirement_rejects_unsupported_older_versions(self) -> None:
        requirement = _pymodbus_requirement()

        self.assertFalse(_allows_version(requirement, "3.11.1"))
        self.assertFalse(_allows_version(requirement, "3.9.2"))
        self.assertFalse(_allows_version(requirement, "3.14.0"))
