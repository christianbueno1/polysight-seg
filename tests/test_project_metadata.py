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

    def test_torch_is_not_a_direct_download(self) -> None:
        package_names = {
            dependency.split("==", maxsplit=1)[0]
            for dependency in self.project["dependencies"]
        }
        self.assertNotIn("torch", package_names)

    def test_required_project_structure_exists(self) -> None:
        required_paths = (
            "configs",
            "docs",
            "scripts",
            "slurm",
            "src/polysight_seg",
            "tests",
            "scripts/smoke_gpu.py",
            "slurm/smoke_gpu.sbatch",
        )
        for relative_path in required_paths:
            with self.subTest(path=relative_path):
                self.assertTrue((PROJECT_ROOT / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
