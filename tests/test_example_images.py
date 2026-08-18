"""Contratos del conjunto pequeño de imágenes para demostración."""

from __future__ import annotations

import csv
import hashlib
import unittest
from collections import defaultdict
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = PROJECT_ROOT / "examples"
EXPECTED_MAIN16 = {
    "bbps-0-1",
    "bbps-2-3",
    "cecum",
    "dyed-lifted-polyps",
    "dyed-resection-margins",
    "esophagitis-a",
    "esophagitis-b-d",
    "impacted-stool",
    "polyps",
    "pylorus",
    "retroflex-rectum",
    "retroflex-stomach",
    "ulcerative-colitis-grade-1",
    "ulcerative-colitis-grade-2",
    "ulcerative-colitis-grade-3",
    "z-line",
}


class ExampleImagesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (EXAMPLES_ROOT / "manifest.csv").open(newline="", encoding="utf-8") as file:
            cls.rows = list(csv.DictReader(file))

    def test_manifest_covers_main16_and_three_segmentation_pairs(self) -> None:
        classification = [row for row in self.rows if row["task"] == "classification"]
        self.assertEqual(len(classification), 16)
        self.assertEqual({row["label"] for row in classification}, EXPECTED_MAIN16)

        segmentation = [row for row in self.rows if row["task"] == "segmentation"]
        self.assertEqual(len(segmentation), 6)
        self.assertEqual({row["size_stratum"] for row in segmentation}, {"small", "medium", "large"})
        self.assertTrue(all(row["split"] == "validation" for row in segmentation))

    def test_files_exist_decode_and_match_hashes(self) -> None:
        for row in self.rows:
            with self.subTest(path=row["path"]):
                path = EXAMPLES_ROOT / row["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"])
                with Image.open(path) as image:
                    image.verify()
                    self.assertEqual(image.format, "JPEG")

    def test_segmentation_images_and_masks_have_matching_dimensions(self) -> None:
        pairs: dict[str, dict[str, Path]] = defaultdict(dict)
        for row in self.rows:
            if row["task"] == "segmentation":
                pairs[row["sample_id"]][row["role"]] = EXAMPLES_ROOT / row["path"]

        self.assertEqual(len(pairs), 3)
        for sample_id, roles in pairs.items():
            with self.subTest(sample_id=sample_id):
                self.assertEqual(set(roles), {"image", "mask"})
                with Image.open(roles["image"]) as image, Image.open(roles["mask"]) as mask:
                    self.assertEqual(image.size, mask.size)

    def test_segmentation_examples_retain_validation_assignment(self) -> None:
        assignments = {}
        with (PROJECT_ROOT / "data/processed/kvasir-seg/splits.csv").open(
            newline="", encoding="utf-8"
        ) as file:
            for row in csv.DictReader(file):
                assignments[row["sample_id"]] = (row["split"], row["size_stratum"])

        for row in self.rows:
            if row["task"] == "segmentation":
                self.assertEqual(
                    assignments[row["sample_id"]],
                    (row["split"], row["size_stratum"]),
                )


if __name__ == "__main__":
    unittest.main()
