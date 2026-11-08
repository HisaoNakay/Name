#!/usr/bin/env python3
"""Слить свежесобранные пакеты в индекс бинхоста (Release `binhost`).

merge-index.py PKGDIR OLD_PACKAGES|- OUT_DIR PREFIX

Файлы Release лежат плоско, поэтому PATH каждого нового пакета
(`cat/pn/pf-N.gpkg.tar`) превращается в имя файла `PREFIX-cat__pn__pf-N.gpkg.tar`;
пакет копируется в OUT_DIR под этим именем. Старые записи с тем же CPV
выкидываются, итоговый индекс пишется в OUT_DIR/Packages.
"""
import re
import shutil
import sys
import time
from pathlib import Path


def parse(text):
    blocks = [b for b in text.strip().split("\n\n") if b.strip()]
    def fields(b):
        out = {}
        for line in b.splitlines():
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
        return out
    if not blocks:
        return {}, []
    return fields(blocks[0]), [fields(b) for b in blocks[1:]]


def dump(header, entries):
    def block(d):
        return "\n".join(f"{k}: {v}" for k, v in d.items())
    return "\n\n".join([block(header)] + [block(e) for e in entries]) + "\n"


def main():
    pkgdir, old, out, prefix = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), sys.argv[4]
    out.mkdir(parents=True, exist_ok=True)
    header, new = parse((pkgdir / "Packages").read_text())
    _, kept = parse(Path(old).read_text()) if old != "-" else ({}, [])

    for e in new:
        name = prefix + "-" + re.sub(r"[^A-Za-z0-9._-]", "_", e["PATH"].replace("/", "__"))
        shutil.copy2(pkgdir / e["PATH"], out / name)
        e["PATH"] = name
        print(f"+ {e['CPV']}  ->  {name}")

    fresh = {e["CPV"] for e in new}
    kept = [e for e in kept if e.get("CPV") not in fresh]
    entries = sorted(kept + new, key=lambda e: e["CPV"])
    header["PACKAGES"] = str(len(entries))
    header["TIMESTAMP"] = str(int(time.time()))
    (out / "Packages").write_text(dump(header, entries))
    print(f"в индексе {len(entries)} пакетов ({len(new)} новых)")


if __name__ == "__main__":
    main()
