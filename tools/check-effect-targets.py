#!/usr/bin/env python3
"""Validate mod policy/event effect targets against vanilla data."""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = (ROOT / "reference" / "game_path.txt").read_text(encoding="utf-8").strip()
GAME_P = Path(GAME)

# Collect known names from vanilla simulation CSVs and related files
known = set()
sim_dir = GAME_P / "data" / "simulation"
for path in sim_dir.rglob("*"):
    if path.suffix.lower() not in {".csv", ".txt"}:
        continue
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]{2,})\b", text):
        known.add(m.group(1))

# Also policy names from vanilla
pol_path = sim_dir / "policies.csv"
if pol_path.exists():
    for row in csv.reader(pol_path.open(encoding="utf-8", errors="ignore")):
        if len(row) > 1 and row[0] == "#":
            known.add(row[1])

# Known voter groups / specials often used
known.update(
    {
        "_All_",
        "_prereq_eu",
        "_random_",
        "_percept_trust",
        "GDP",
        "Debt",
        "Crime",
        "Health",
        "Technology",
        "Environment",
        "Immigration",
        "IllegalImmigration",
        "Homelessness",
        "Unemployment",
        "PovertyRate",
        "PrivateHousing",
        "FoodPrice",
        "Agriculture",
        "Tourism",
        "Farmers",
        "Capitalist",
        "Poor",
        "MiddleIncome",
        "Liberal",
        "Socialist",
        "Conservatives",
        "Patriot",
        "Parents",
        "SelfEmployed",
        "ForeignRelations",
        "InternationalTrade",
        "EnergyEfficiency",
        "CO2Emissions",
        "AverageTemperature",
        "HealthcareDemand",
        "FakeNews",
        "RacialTension",
        "Equality",
        "Democracy",
        "Stability",
        "Corruption",
    }
)

mod_pol = ROOT / "ModernPressureEU" / "data" / "simulation" / "policies.csv"
bad_pol = []
targets = set()
for row in csv.reader(mod_pol.open(encoding="utf-8")):
    if not row or row[0] != "#":
        continue
    pid = row[1]
    # effects start after #Effects marker
    try:
        idx = row.index("#Effects")
    except ValueError:
        continue
    for cell in row[idx + 1 :]:
        if not cell or not cell.strip():
            continue
        name = cell.split(",")[0].strip().strip('"')
        if not name or name == "#Effects":
            continue
        targets.add((pid, name))
        if name not in known:
            bad_pol.append((pid, name))

print("=== BAD POLICY EFFECT TARGETS ===")
for pid, name in sorted(bad_pol):
    print(f"{pid}: {name}")
if not bad_pol:
    print("(none)")

# Event CreateGrudge / influence names
ev_dir = ROOT / "ModernPressureEU" / "data" / "simulation" / "events"
bad_ev = []
for path in sorted(ev_dir.glob("*.txt")):
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"CreateGrudge\(([A-Za-z_][A-Za-z0-9_]*)", text):
        name = m.group(1)
        # event Names are ok even if not in known (self/sibling)
        if name not in known and not (ev_dir / f"{name}.txt").exists():
            # also allow v1+v2 event names present as files
            bad_ev.append((path.name, f"CreateGrudge:{name}"))
    for line in text.splitlines():
        if "=" not in line or line.strip().startswith("["):
            continue
        # influences: N = Name,...
        m = re.match(r"\s*\d+\s*=\s*([^,]+)", line)
        if not m:
            continue
        name = m.group(1).strip()
        if name in {"_random_", "_prereq_"}:
            continue
        if name.startswith("_prereq"):
            continue
        if name not in known and not (ev_dir / f"{name}.txt").exists():
            bad_ev.append((path.name, f"influence:{name}"))

print("=== BAD EVENT REFS ===")
for f, name in sorted(set(bad_ev)):
    print(f"{f}: {name}")
if not bad_ev:
    print("(none)")

print(f"known_approx={len(known)} policy_targets={len(targets)}")
