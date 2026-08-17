"""Pruebas ligeras de metadatos que no requieren PyTorch."""

from __future__ import annotations

import sys
import tomllib
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import polysight_seg  # noqa: E402


class ProjectMetadataTest(unittest.TestCase):
    """Mantiene alineados el paquete y su configuración."""

    @classmethod
    def setUpClass(cls) -> None:
        with (PROJECT_ROOT / "pyproject.toml").open("rb") as file:
            cls.project = tomllib.load(file)["project"]

    def test_package_version_matches_project(self) -> None:
        self.assertEqual(polysight_seg.__version__, self.project["version"])

    def test_python_is_limited_to_cedia_version(self) -> None:
        self.assertEqual(self.project["requires-python"], ">=3.11,<3.12")


if __name__ == "__main__":
    unittest.main()
