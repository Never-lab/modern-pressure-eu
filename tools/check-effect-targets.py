#!/usr/bin/env python3
"""Fail if mod policies/events reference unknown Democracy 4 simulation objects."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = (
    (ROOT / "reference" / "game_path.txt")
    .read_text(encoding="utf-8-sig")
    .strip()
    .strip("\ufeff")
)
GAME_P = Path(GAME)
MOD = ROOT / "ModernPressureEU"


def load_known() -> set[str]:
    known = {
        "_All_",
        "_prereq_eu",
        "_prereq_",
        "_random_",
        "_percept_trust",
        "_effectivedebt_",
        "_globaleconomy_",
        "_global_interest_rates_",
        "_winning_",
        "_difficulty_",
        "_year",
        "_security_",
        "_HighIncome",
        "_LowIncome",
        "_MiddleIncome",
        "_Terrorism",
    }
    sim = GAME_P / "data" / "simulation"
    for fname in (
        "simulation.csv",
        "situations.csv",
        "votertypes.csv",
        "pressuregroups.csv",
        "policies.csv",
    ):
        path = sim / fname
        for row in csv.reader(path.open(encoding="utf-8", errors="ignore")):
            if row and row[0] == "#" and len(row) > 1:
                known.add(row[1])
    for folder in (sim / "events", MOD / "data" / "simulation" / "events"):
        if not folder.exists():
            continue
        for path in folder.glob("*.txt"):
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()[:10]:
                if line.strip().lower().startswith("name"):
                    known.add(line.split("=", 1)[1].strip())
                    break
    return known


def main() -> int:
    known = load_known()
    bad: list[str] = []

    pol = MOD / "data" / "simulation" / "policies.csv"
    for row in csv.reader(pol.open(encoding="utf-8")):
        if not row or row[0] != "#":
            continue
        pid = row[1]
        if "#Effects" not in row:
            bad.append(f"policy {pid}: missing #Effects")
            continue
        idx = row.index("#Effects")
        for cell in row[idx + 1 :]:
            if not cell.strip():
                continue
            name = cell.split(",")[0].strip().strip('"')
            if name and name not in known:
                bad.append(f"policy {pid}: {name}")

    for path in sorted((MOD / "data" / "simulation" / "events").glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"CreateGrudge\(([A-Za-z_][A-Za-z0-9_]*)", text):
            if m.group(1) not in known:
                bad.append(f"grudge {path.name}: {m.group(1)}")
        for line in text.splitlines():
            m = re.match(r"\s*\d+\s*=\s*([^,]+)", line)
            if not m:
                continue
            name = m.group(1).strip()
            if name in {"_random_", "_prereq_", "_winning_", "_difficulty_"}:
                continue
            if name.startswith("_prereq"):
                continue
            if name not in known:
                bad.append(f"influence {path.name}: {name}")

    if bad:
        print("INVALID_TARGETS")
        for item in sorted(set(bad)):
            print(item)
        return 1
    print("TARGETS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
