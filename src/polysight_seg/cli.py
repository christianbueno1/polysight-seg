"""Punto de entrada ligero que no importa PyTorch."""

from polysight_seg import __version__


def main() -> None:
    """Muestra la versión sin cargar dependencias de entrenamiento."""
    print(f"polysight-seg {__version__}")


if __name__ == "__main__":
    main()
