"""Contratos estáticos de los notebooks reproducibles."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = {
    "inference": PROJECT_ROOT / "notebooks/01-polysight-seg-inference-verification.ipynb",
    "training": PROJECT_ROOT / "notebooks/02-polysight-seg-training-reproduction.ipynb",
}
RELEASE_REF = "2bf2c5a874272ecd6ccd24b936af578f4e637c82"


class NotebookContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.notebooks = {
            name: json.loads(path.read_text(encoding="utf-8"))
            for name, path in NOTEBOOKS.items()
        }
        cls.sources = {
            name: "\n".join(
                "".join(cell.get("source", [])) for cell in notebook["cells"]
            )
            for name, notebook in cls.notebooks.items()
        }

    def test_notebooks_are_clean_and_use_supported_schema(self) -> None:
        for name, notebook in self.notebooks.items():
            with self.subTest(notebook=name):
                self.assertEqual(notebook["nbformat"], 4)
                for cell in notebook["cells"]:
                    if cell["cell_type"] == "code":
                        self.assertIsNone(cell["execution_count"])
                        self.assertEqual(cell["outputs"], [])

    def test_notebooks_clone_a_fixed_commit(self) -> None:
        for name, source in self.sources.items():
            with self.subTest(notebook=name):
                self.assertIn(f"REPO_REF = '{RELEASE_REF}'", source)
                self.assertIn("git', 'clone', '--no-checkout'", source)
                self.assertIn("'checkout', '--detach', REPO_REF", source)

    def test_inference_notebook_reuses_production_code_and_hash(self) -> None:
        source = self.sources["inference"]
        self.assertIn("from polysight_seg.inference import load_verified_model", source)
        self.assertIn("from polysight_seg.inference import predict_image", source)
        self.assertIn("EXPECTED_CHECKPOINT_SHA256", source)
        self.assertIn("scripts/validate_local.sh", source)

    def test_training_notebook_uses_existing_pipeline_and_disables_test(self) -> None:
        source = self.sources["training"]
        for script in (
            "scripts/prepare_dataset.py",
            "scripts/validate_dataset.py",
            "scripts/generate_manifest.py",
            "scripts/generate_splits.py",
            "scripts/validate_splits.py",
            "scripts/train.py",
        ):
            with self.subTest(script=script):
                self.assertIn(script, source)
        self.assertIn("RUN_FULL_EXPERIMENT = False", source)
        self.assertIn("RUN_TEST_EVALUATION = False", source)
        self.assertNotIn("scripts/evaluate.py", source)

    def test_notebooks_do_not_contain_secrets_or_personal_paths(self) -> None:
        forbidden = ("/home/chris", "ghp_", "github_pat_", "PRIVATE_KEY", "PASSWORD=")
        for name, source in self.sources.items():
            for value in forbidden:
                with self.subTest(notebook=name, value=value):
                    self.assertNotIn(value, source)


if __name__ == "__main__":
    unittest.main()
