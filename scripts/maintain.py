#!/usr/bin/env python3
"""Generate immutable slots and synchronize them with the official HA app."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_BASE = "https://raw.githubusercontent.com/zigbee2mqtt/hassio-zigbee2mqtt"
TEXT_FILES = ("CHANGELOG.md", "DOCS.md", "README.md")
BINARY_FILES = ("icon.png", "logo.png")
SLOT_RE = re.compile(r"tmh_zigbee2mqtt_(\d+)$")


def wanted_slots() -> int:
    text = (ROOT / "slots.yaml").read_text(encoding="utf-8")
    match = re.fullmatch(r"\s*slots:\s*(\d+)\s*", text)
    if not match:
        raise ValueError("slots.yaml deve conter somente: slots: N")
    value = int(match.group(1))
    if value < 1 or value > 99:
        raise ValueError("slots deve estar entre 1 e 99")
    return value


def existing_numbers() -> set[int]:
    found = set()
    for path in ROOT.iterdir():
        if path.is_dir() and (match := SLOT_RE.fullmatch(path.name)):
            found.add(int(match.group(1)))
    return found


def download(name: str) -> bytes:
    ref_text = (ROOT / "upstream.yaml").read_text(encoding="utf-8")
    ref_match = re.fullmatch(r"\s*ref:\s*([A-Za-z0-9._/-]+)\s*", ref_text)
    if not ref_match or ".." in ref_match.group(1):
        raise ValueError("upstream.yaml deve conter uma ref Git válida")
    upstream = f"{UPSTREAM_BASE}/{ref_match.group(1)}/zigbee2mqtt"
    request = urllib.request.Request(
        f"{upstream}/{name}", headers={"User-Agent": "tmh-zigbee2mqtt-sync"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def transformed_config(source: bytes, number: int) -> bytes:
    config = json.loads(source)
    suffix = f"{number:02d}"
    config["name"] = f"TMH Zigbee2MQTT {suffix}"
    config["slug"] = f"tmh_zigbee2mqtt_{suffix}"
    config["description"] = f"Instância isolada {suffix} do Zigbee2MQTT"
    repository_text = (ROOT / "repository.yaml").read_text(encoding="utf-8")
    url_match = re.search(r"^url:\s*(\S+)\s*$", repository_text, re.MULTILINE)
    if not url_match:
        raise ValueError("repository.yaml precisa conter uma linha 'url: https://...'")
    config["url"] = url_match.group(1)
    config.setdefault("options", {})["data_path"] = "/addon_config"
    # A fixed host port would prevent two slots from running simultaneously.
    # Keep the container port available, but require an explicit, unique host
    # port only for installations that enable socat.
    if "8485/tcp" in config.get("ports", {}):
        config["ports"]["8485/tcp"] = None
    return (json.dumps(config, indent=2, ensure_ascii=False) + "\n").encode()


def write_if_changed(path: Path, content: bytes) -> bool:
    if path.exists() and path.read_bytes() == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    total = wanted_slots()
    existing = existing_numbers()
    if existing and total < max(existing):
        raise ValueError(
            f"Recusado: slots não pode diminuir de {max(existing)} para {total}; "
            "slugs publicados são imutáveis."
        )

    remote = {"config.json": download("config.json")}
    for name in (*TEXT_FILES, *BINARY_FILES):
        remote[name] = download(name)

    changed = []
    for number in range(1, total + 1):
        directory = ROOT / f"tmh_zigbee2mqtt_{number:02d}"
        files = {"config.json": transformed_config(remote["config.json"], number)}
        files.update({name: remote[name] for name in (*TEXT_FILES, *BINARY_FILES)})
        for name, content in files.items():
            target = directory / name
            if not target.exists() or target.read_bytes() != content:
                changed.append(str(target.relative_to(ROOT)))
                if not args.check:
                    write_if_changed(target, content)

    if changed:
        print("Arquivos desatualizados:")
        print("\n".join(f"- {item}" for item in changed))
        return 1 if args.check else 0
    print("Tudo atualizado.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERRO: {error}", file=sys.stderr)
        raise SystemExit(2)
