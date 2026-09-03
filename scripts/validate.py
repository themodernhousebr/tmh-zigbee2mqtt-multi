#!/usr/bin/env python3
"""Offline checks for the generated Home Assistant app repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SLOT_RE = re.compile(r"tmh_zigbee2mqtt_(\d{2})$")


def fail(message: str) -> None:
    print(f"ERRO: {message}", file=sys.stderr)
    raise SystemExit(1)


text = (ROOT / "slots.yaml").read_text(encoding="utf-8")
match = re.fullmatch(r"\s*slots:\s*(\d+)\s*", text)
if not match:
    fail("slots.yaml inválido")
total = int(match.group(1))
if total < 1 or total > 99:
    fail("slots deve estar entre 1 e 99")

repository_text = (ROOT / "repository.yaml").read_text(encoding="utf-8")
url_match = re.search(r"^url:\s*(\S+)\s*$", repository_text, re.MULTILINE)
if not url_match:
    fail("repository.yaml não contém url")
repository_url = url_match.group(1)
parsed_url = urlparse(repository_url)
if parsed_url.scheme != "https" or parsed_url.netloc != "github.com":
    fail("repository.yaml deve apontar para uma URL HTTPS do GitHub")

expected = {f"tmh_zigbee2mqtt_{number:02d}" for number in range(1, total + 1)}
actual = {path.name for path in ROOT.iterdir() if path.is_dir() and SLOT_RE.fullmatch(path.name)}
if actual != expected:
    fail(f"slots encontrados não correspondem a 1..{total}")

versions = set()
slugs = set()
for name in sorted(actual):
    path = ROOT / name
    config = json.loads((path / "config.json").read_text(encoding="utf-8"))
    for required in ("name", "version", "slug", "arch", "image", "options", "schema"):
        if required not in config:
            fail(f"{name}: campo obrigatório ausente: {required}")
    if config["slug"] != name:
        fail(f"{name}: slug divergente")
    if config["slug"] in slugs:
        fail(f"slug duplicado: {config['slug']}")
    if config["options"].get("data_path") != "/addon_config":
        fail(f"{name}: data_path não está isolado em /addon_config")
    if config.get("url") != repository_url:
        fail(f"{name}: URL não corresponde a repository.yaml")
    if not config["image"].startswith("ghcr.io/zigbee2mqtt/"):
        fail(f"{name}: não usa a imagem oficial")
    if config.get("ports", {}).get("8485/tcp") is not None:
        fail(f"{name}: porta socat fixa impediria múltiplas instâncias")
    for required_file in ("README.md", "DOCS.md", "CHANGELOG.md", "icon.png", "logo.png"):
        if not (path / required_file).is_file():
            fail(f"{name}: arquivo ausente: {required_file}")
    slugs.add(config["slug"])
    versions.add(config["version"])

if len(versions) != 1:
    fail(f"os slots têm versões diferentes: {sorted(versions)}")

print(f"OK: {total} slots únicos, versão {versions.pop()}, todos isolados.")
