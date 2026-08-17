"""Smoke test de PyTorch/CUDA destinado exclusivamente a CEDIA HPC."""

from __future__ import annotations

import json
import platform

import torch


def main() -> None:
    """Verifica CUDA mediante una operación con forward y backward."""
    environment = {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "cuda_build": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "cudnn": torch.backends.cudnn.version(),
        "device_count": torch.cuda.device_count(),
    }

    if not torch.cuda.is_available():
        print(json.dumps(environment, indent=2, sort_keys=True))
        raise RuntimeError("CUDA no está disponible dentro del trabajo Slurm")

    device = torch.device("cuda:0")
    environment["device"] = torch.cuda.get_device_name(device)

    model = torch.nn.Conv2d(3, 1, kernel_size=3, padding=1).to(device)
    inputs = torch.randn(2, 3, 128, 128, device=device, requires_grad=True)
    outputs = model(inputs)
    loss = outputs.square().mean()
    loss.backward()
    torch.cuda.synchronize(device)

    if model.weight.grad is None or not torch.isfinite(loss):
        raise RuntimeError("El ciclo forward/backward produjo un resultado inválido")

    environment["smoke_loss"] = loss.item()
    environment["status"] = "ok"
    print(json.dumps(environment, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
