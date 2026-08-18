"""Valida que los enlaces locales de Markdown apunten a rutas existentes."""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")


class MarkdownLinksTest(unittest.TestCase):
    """Impide entregar referencias locales rotas en archivos versionados."""

    def test_all_versioned_local_links_exist(self) -> None:
        result = subprocess.run(
            ["git", "ls-files", "*.md"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        failures: list[str] = []
        for relative_path in result.stdout.splitlines():
            document_path = PROJECT_ROOT / relative_path
            if not document_path.is_file():
                continue
            text = document_path.read_text(encoding="utf-8")
            for line_number, line in enumerate(text.splitlines(), start=1):
                for match in LINK_PATTERN.finditer(line):
                    target = match.group(1).strip().strip("<>")
                    if not target or target.startswith(EXTERNAL_PREFIXES):
                        continue
                    target = unquote(target.split("#", maxsplit=1)[0])
                    resolved = (document_path.parent / target).resolve()
                    if not resolved.exists():
                        failures.append(f"{relative_path}:{line_number} -> {target}")
        self.assertEqual([], failures, "Enlaces locales rotos:\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
