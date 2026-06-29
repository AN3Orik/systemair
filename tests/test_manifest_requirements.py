"""Regression tests for package requirements declared in the integration manifest."""

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
    version_tuple = _version_tuple(version)

    for raw_specifier in requirement.removeprefix("pymodbus").split(","):
        specifier = raw_specifier.strip()
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

        if specifier.startswith("<") and version_tuple >= _version_tuple(specifier[1:]):
            return False

    return True


class ManifestRequirementsTest(unittest.TestCase):
    """Regression coverage for the integration manifest requirements."""

    def test_pymodbus_requirement_allows_supported_versions(self) -> None:
        """The manifest must allow both currently supported Home Assistant dependency sets."""
        requirement = _pymodbus_requirement()

        assert _allows_version(requirement, "3.11.2")  # noqa: S101
        assert _allows_version(requirement, "3.13.1")  # noqa: S101

    def test_pymodbus_requirement_rejects_unsupported_older_versions(self) -> None:
        """The manifest should not widen support below the declared Home Assistant baseline."""
        requirement = _pymodbus_requirement()

        assert not _allows_version(requirement, "3.11.1")  # noqa: S101
        assert not _allows_version(requirement, "3.9.2")  # noqa: S101
        assert not _allows_version(requirement, "3.14.0")  # noqa: S101
