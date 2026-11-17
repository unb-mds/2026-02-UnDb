"""Snapshot local, não é lockfile de produção. Executar com a venv da revisão."""

import json
import argparse
import sys
from importlib.metadata import distribution
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

raiz = Path(__file__).resolve().parents[4]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
saida = parser.parse_args().output_dir
saida.mkdir(parents=True, exist_ok=True)
pendentes = [Requirement(linha) for linha in (raiz / "backend/requirements.txt").read_text(encoding="utf-8").splitlines() if linha.strip() and not linha.startswith("#")]
vistos = set()
pacotes = {}
while pendentes:
    req = pendentes.pop()
    nome = canonicalize_name(req.name)
    chave = (nome, tuple(sorted(req.extras)))
    if chave in vistos:
        continue
    vistos.add(chave)
    dist = distribution(nome)
    pacotes[nome] = dist.version
    for linha in dist.requires or []:
        sub = Requirement(linha)
        if sub.marker is None or any(sub.marker.evaluate({"extra": extra}) for extra in ["", *req.extras]):
            pendentes.append(sub)
snapshot = {"python": sys.version.split()[0], "platform": sys.platform, "packages": dict(sorted(pacotes.items()))}
(saida / "python-resolvido.json").write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
(saida / "python-resolvido.txt").write_text("".join(f"{k}=={v}\n" for k, v in sorted(pacotes.items())), encoding="utf-8")
lock = json.loads((raiz / "frontend/package-lock.json").read_text(encoding="utf-8"))
(saida / "frontend-resolvido.json").write_text(json.dumps({"lockfileVersion": lock["lockfileVersion"], "packages": {k: {"version": v.get("version"), "dev": v.get("dev", False), "optional": v.get("optional", False)} for k,v in lock["packages"].items() if k}}, indent=2) + "\n", encoding="utf-8")
print(f"Snapshot: {len(pacotes)} pacotes Python; {len(lock['packages']) - 1} entradas npm.")
