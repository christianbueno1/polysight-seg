"""Pruebas ligeras para preparación de datos, sin PyTorch."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from polysight_seg.data.archive import SOURCE_MARKER, extract_dataset  # noqa: E402
from polysight_seg.data.masks import binarize_mask  # noqa: E402


class MaskBinarizationTest(unittest.TestCase):
    def test_threshold_maps_to_strict_binary_values(self) -> None:
        mask = Image.new("L", (4, 1))
        mask.putdata([0, 127, 128, 255])

        binary = binarize_mask(mask)

        self.assertEqual(list(binary.tobytes()), [0, 0, 255, 255])


class ArchiveExtractionTest(unittest.TestCase):
    def test_extraction_is_idempotent_for_same_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "dataset.zip"
            output = root / "raw" / "kvasir-seg"
            with zipfile.ZipFile(archive, "w") as file:
                file.writestr("segmented-images/images/example.jpg", b"image")
                file.writestr("segmented-images/masks/example.jpg", b"mask")

            self.assertEqual(extract_dataset(archive, output), "extracted")
            self.assertEqual(extract_dataset(archive, output), "unchanged")
            marker = json.loads((output / SOURCE_MARKER).read_text(encoding="utf-8"))
            self.assertEqual(marker["extracted_files"], 2)

    def test_extraction_rejects_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "unsafe.zip"
            output = root / "raw" / "kvasir-seg"
            with zipfile.ZipFile(archive, "w") as file:
                file.writestr("segmented-images/../escape.txt", b"unsafe")

            with self.assertRaisesRegex(ValueError, "insegura"):
                extract_dataset(archive, output)
            self.assertFalse(output.exists())
            self.assertFalse((root / "escape.txt").exists())


if __name__ == "__main__":
    unittest.main()
