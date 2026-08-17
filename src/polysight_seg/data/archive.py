"""Extracción segura e idempotente del archivo oficial de Kvasir-SEG."""

from __future__ import annotations

import hashlib
import json
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


SOURCE_MARKER = ".source.json"
EXPECTED_ROOT = "segmented-images"
MAX_UNCOMPRESSED_BYTES = 2 * 1024**3


def sha256_file(path: Path) -> str:
    """Calcula SHA-256 en bloques para no cargar el archivo completo en memoria."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _relative_member(name: str) -> Path | None:
    """Valida una entrada ZIP y elimina el directorio raíz esperado."""
    if "\\" in name:
        raise ValueError(f"Ruta ZIP con separador no permitido: {name!r}")

    member = PurePosixPath(name)
    if member.is_absolute() or ".." in member.parts:
        raise ValueError(f"Ruta ZIP insegura: {name!r}")
    if not member.parts or member.parts[0] != EXPECTED_ROOT:
        raise ValueError(f"Entrada fuera de {EXPECTED_ROOT}/: {name!r}")
    if len(member.parts) == 1:
        return None
    return Path(*member.parts[1:])


def _is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = info.external_attr >> 16
    return stat.S_IFMT(mode) == stat.S_IFLNK


def extract_dataset(archive: Path, output: Path) -> str:
    """Extrae el dataset de forma atómica o devuelve `unchanged` si ya coincide."""
    archive = archive.resolve(strict=True)
    output = output.resolve()
    archive_sha256 = sha256_file(archive)
    marker_path = output / SOURCE_MARKER

    if output.exists():
        if not marker_path.is_file():
            raise FileExistsError(f"El destino existe sin {SOURCE_MARKER}: {output}")
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        if marker.get("sha256") == archive_sha256:
            return "unchanged"
        raise FileExistsError("El destino fue creado desde un archivo con otro SHA-256")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as source:
        entries = source.infolist()
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)):
            raise ValueError("El ZIP contiene nombres de entrada duplicados")
        if sum(entry.file_size for entry in entries) > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("El tamaño descomprimido supera el límite de seguridad")

        with tempfile.TemporaryDirectory(
            dir=output.parent, prefix=".kvasir-seg-"
        ) as temporary_directory:
            staging = Path(temporary_directory)
            extracted_files = 0

            for entry in entries:
                relative = _relative_member(entry.filename)
                if relative is None:
                    continue
                if _is_symlink(entry):
                    raise ValueError(f"No se permiten enlaces en el ZIP: {entry.filename}")

                destination = staging / relative
                if entry.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue

                destination.parent.mkdir(parents=True, exist_ok=True)
                with source.open(entry) as input_file, destination.open("xb") as output_file:
                    shutil.copyfileobj(input_file, output_file)
                extracted_files += 1

            marker = {
                "schema_version": 1,
                "source_file": archive.name,
                "source_size_bytes": archive.stat().st_size,
                "sha256": archive_sha256,
                "zip_entries": len(entries),
                "extracted_files": extracted_files,
            }
            (staging / SOURCE_MARKER).write_text(
                json.dumps(marker, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            staging.replace(output)

    return "extracted"
