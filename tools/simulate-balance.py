#!/usr/bin/env python3
"""Monte Carlo balance sim for ModernPressureEU events (+ light policy pressure)."""
from __future__ import annotations

import argparse
import csv
import random
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV_DIR = ROOT / "ModernPressureEU" / "data" / "simulation" / "events"
POL_PATH = ROOT / "ModernPressureEU" / "data" / "simulation" / "policies.csv"

CLUSTERS = {
    "climate_v1": {"HeatGridFailure", "EnergyPriceSpike"},
    "housing_v1": {"RentStrikeWave", "MortgageStress"},
    "tech_v1": {"AILayoffBacklash", "DeepfakeScandal"},
    "mig_v1": {"BorderProcessingCollapse"},
    "health_v1": {"HospitalWinterCrisis"},
    "climate_v2": {"CropFailureDrought", "CoastalFloodShock"},
    "housing_v2": {"HomelessCampCrisis", "LandlordExodus"},
    "mig_v2": {"ReceptionCenterRiot", "SmugglerCorridorSpike"},
    "tech_v2": {"PublicDataLeak", "AutomationStrike"},
    "health_v2": {"AmbulanceGridlock", "CareHomeOutbreak"},
    "cross": {"CostOfLivingMarch", "EUFiscalWarning"},
}
HEAVY = {"climate_v1", "climate_v2", "housing_v1", "housing_v2", "mig_v1", "mig_v2"}
BURST_PAIRS = [
    ("CropFailureDrought", "CoastalFloodShock"),
    ("HomelessCampCrisis", "LandlordExodus"),
    ("ReceptionCenterRiot", "SmugglerCorridorSpike"),
    ("HeatGridFailure", "EnergyPriceSpike"),
    ("RentStrikeWave", "MortgageStress"),
]

# Baseline EU mid-mandate pressure (0..1)
BASE_STATE = {
    "AverageTemperature": 0.55,
    "Environment": 0.45,
    "EnergyEfficiency": 0.45,
    "OilPrice": 0.50,
    "PrivateEnergy": 0.55,
    "Technology": 0.55,
    "IndustrialAutomation": 0.45,
    "Unemployment": 0.40,
    "FakeNews": 0.40,
    "Democracy": 0.55,
    "_percept_trust": 0.50,
    "Immigration": 0.50,
    "IllegalImmigration": 0.45,
    "RacialTension": 0.40,
    "CrimeRate": 0.45,
    "Homelessness": 0.45,
    "PrivateHousing": 0.50,
    "PovertyRate": 0.45,
    "DebtCrisis": 0.35,
    "_global_interest_rates_": 0.45,
    "_effectivedebt_": 0.50,
    "GDP": 0.55,
    "Health": 0.50,
    "HealthcareDemand": 0.50,
    "HospitalOvercrowding": 0.40,
    "FoodPrice": 0.45,
    "ForeignRelations": 0.55,
    "Tourism": 0.50,
}


@dataclass
class EventDef:
    name: str
    influences: list  # (kind, payload)
    grudges: list  # (target, amount, inertia)


@dataclass
class SimResult:
    fires: list  # (turn, name)
    policy_pressure: float


def parse_events(scale_random: float = 1.0) -> dict[str, EventDef]:
    out = {}
    for path in EV_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        name_m = re.search(r"(?im)^Name\s*=\s*(\S+)", text)
        if not name_m:
            continue
        name = name_m.group(1).strip()
        grudges = []
        impl = re.search(r"(?im)^OnImplement\s*=\s*(.+)$", text)
        if impl:
            for g in re.finditer(
                r"CreateGrudge\(([A-Za-z_][A-Za-z0-9_]*),\s*([-\d.]+),\s*([-\d.]+)\)",
                impl.group(1),
            ):
                grudges.append((g.group(1), float(g.group(2)), float(g.group(3))))
        influences = []
        for line in text.splitlines():
            m = re.match(r"\s*\d+\s*=\s*(.+)$", line)
            if not m:
                continue
            parts = [p.strip() for p in m.group(1).split(",")]
            head = parts[0]
            if head == "_random_":
                lo, hi = float(parts[1]), float(parts[2])
                mid = (lo + hi) / 2
                half = (hi - lo) / 2 * scale_random
                influences.append(("random", (mid - half, mid + half)))
            elif head == "_prereq_":
                influences.append(("prereq", parts[1] if len(parts) > 1 else ""))
            else:
                expr = ",".join(parts[1:]) if len(parts) > 1 else "0"
                influences.append(("expr", (head, expr)))
        out[name] = EventDef(name=name, influences=influences, grudges=grudges)
    return out


def eval_expr(expr: str, x: float) -> float:
    # Supports a+(b*x), a-(b*x), a+(b*x)^n approximations as plain a±b*x
    expr = expr.strip()
    # strip trailing ,inertia if present as third field already removed
    expr = expr.split(",")[0]
    try:
        return float(eval(expr.replace("^", "**"), {"__builtins__": {}}, {"x": x}))
    except Exception:
        return 0.0


def cluster_of(name: str) -> str:
    for c, members in CLUSTERS.items():
        if name in members:
            return c
    return "other"


def run_one(
    events: dict[str, EventDef],
    rng: random.Random,
    turns: int = 60,
    eval_every: int = 3,
    fire_threshold: float = 0.62,
    max_fires_per_eval: int = 1,
) -> SimResult:
    state = dict(BASE_STATE)
    # mild drift / scenario noise
    for k in state:
        state[k] = min(0.95, max(0.05, state[k] + rng.uniform(-0.08, 0.12)))
    # optional policy stress: raise debt / housing / migration pressure
    if rng.random() < 0.7:
        state["_effectivedebt_"] = min(0.9, state["_effectivedebt_"] + 0.15)
        state["Homelessness"] = min(0.9, state["Homelessness"] + 0.10)
        state["AverageTemperature"] = min(0.9, state["AverageTemperature"] + 0.08)

    event_mods: dict[str, float] = defaultdict(float)  # additive chance mods from grudges
    fires: list[tuple[int, str]] = []

    for turn in range(1, turns + 1):
        # decay event mods toward 0
        for k in list(event_mods.keys()):
            event_mods[k] *= 0.92
            if abs(event_mods[k]) < 0.01:
                del event_mods[k]
        # world drift
        state["AverageTemperature"] = min(0.95, state["AverageTemperature"] + 0.002)
        state["GDP"] = max(0.15, state["GDP"] + rng.uniform(-0.01, 0.008))
        state["_effectivedebt_"] = min(0.95, max(0.1, state["_effectivedebt_"] + rng.uniform(-0.005, 0.01)))

        if turn % eval_every != 0:
            continue

        scored = []
        for name, ed in events.items():
            # _prereq_ is a gate in D4, not a +1 chance term
            gated = True
            chance = event_mods.get(name, 0.0)
            for kind, payload in ed.influences:
                if kind == "prereq":
                    if payload != "_prereq_eu":
                        gated = False
                    continue
                if kind == "random":
                    lo, hi = payload
                    chance += rng.uniform(lo, hi)
                elif kind == "expr":
                    sim, expr = payload
                    x = state.get(sim, 0.4)
                    chance += eval_expr(expr, x)
            if not gated:
                continue
            chance = max(0.0, min(1.0, chance))
            scored.append((chance, name))

        scored.sort(reverse=True)
        fired_this = 0
        for chance, name in scored:
            if fired_this >= max_fires_per_eval:
                break
            if chance < fire_threshold:
                continue
            # probabilistic fire weighted by surplus over threshold
            p = min(0.95, 0.35 + (chance - fire_threshold))
            if rng.random() > p:
                continue
            fires.append((turn, name))
            fired_this += 1
            # apply grudges
            for target, amount, inertia in events[name].grudges:
                if target in events:
                    # negative amount suppresses; mild positive shouldn't boost much
                    event_mods[target] += amount * (0.6 + 0.4 * inertia)
                elif target in state:
                    state[target] = min(0.95, max(0.05, state[target] + amount * 0.25))

    # policy pressure proxy: cost of introducing half the pack at mid slider
    pressure = 0.0
    for row in csv.reader(POL_PATH.open(encoding="utf-8")):
        if not row or row[0] != "#":
            continue
        try:
            minc, maxc = float(row[11]), float(row[12])
            pressure += (minc + maxc) / 2 / 10000.0
        except Exception:
            pass
    return SimResult(fires=fires, policy_pressure=pressure)


def analyze(results: list[SimResult]) -> dict:
    n = len(results)
    counts = Counter()
    cluster_counts = Counter()
    gaps = []
    bursts = 0
    runs_with_burst = 0
    multi_heavy_same_turn = 0
    events_per_run = []
    co = Counter()  # pairwise co-occurrence same run

    for res in results:
        events_per_run.append(len(res.fires))
        names = [nm for _, nm in res.fires]
        for nm in names:
            counts[nm] += 1
            cluster_counts[cluster_of(nm)] += 1
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                co[tuple(sorted((a, b)))] += 1
        turns = [t for t, _ in res.fires]
        for i in range(1, len(turns)):
            gaps.append(turns[i] - turns[i - 1])
        # burst: sibling pair within 6 turns
        run_burst = False
        by_name = defaultdict(list)
        for t, nm in res.fires:
            by_name[nm].append(t)
        for a, b in BURST_PAIRS:
            for ta in by_name.get(a, []):
                for tb in by_name.get(b, []):
                    if abs(ta - tb) <= 6:
                        bursts += 1
                        run_burst = True
        if run_burst:
            runs_with_burst += 1
        # same eval turn two heavy clusters
        by_turn = defaultdict(list)
        for t, nm in res.fires:
            by_turn[t].append(nm)
        for t, nms in by_turn.items():
            clusters = {cluster_of(x) for x in nms}
            if len(clusters & HEAVY) >= 2:
                multi_heavy_same_turn += 1

    return {
        "runs": n,
        "mean_events": statistics.mean(events_per_run) if events_per_run else 0,
        "p50_events": statistics.median(events_per_run) if events_per_run else 0,
        "mean_gap": statistics.mean(gaps) if gaps else None,
        "burst_pair_hits": bursts,
        "runs_with_burst_pct": 100.0 * runs_with_burst / n,
        "multi_heavy_same_turn": multi_heavy_same_turn,
        "event_counts": counts,
        "cluster_counts": cluster_counts,
        "cooccurrence_top": co.most_common(15),
        "policy_pressure": results[0].policy_pressure if results else 0,
    }


def print_report(a: dict) -> None:
    print("=== MONTE CARLO SUMMARY ===")
    print(f"runs={a['runs']} mean_events/run={a['mean_events']:.2f} p50={a['p50_events']:.1f}")
    print(f"mean_gap_turns={a['mean_gap']}")
    print(f"runs_with_burst%={a['runs_with_burst_pct']:.1f} burst_pair_hits={a['burst_pair_hits']}")
    print(f"multi_heavy_same_turn={a['multi_heavy_same_turn']}")
    print(f"policy_cost_pressure_index={a['policy_pressure']:.2f}")
    print("\n=== CLUSTER MATRIX (fires) ===")
    for c, v in sorted(a["cluster_counts"].items(), key=lambda kv: -kv[1]):
        print(f"{c:12} {v:4}")
    print("\n=== EVENT FREQUENCY ===")
    for e, v in a["event_counts"].most_common():
        print(f"{e:28} {v:4}")
    print("\n=== TOP CO-OCCURRENCE (same run) ===")
    for (a1, b1), v in a["cooccurrence_top"]:
        print(f"{a1:24} + {b1:24} {v}")


def suggest_and_apply(a: dict, dry_run: bool = False) -> list[str]:
    """Tune _random_ ranges in event files toward target feel."""
    actions = []
    mean_e = a["mean_events"]
    burst_pct = a["runs_with_burst_pct"]
    multi = a["multi_heavy_same_turn"]
    # Targets for 60-turn / eval every 3 (~20 windows): ~4-7 events/run, burst in >=35% runs, multi-heavy rare
    scale = 1.0
    if mean_e > 9:
        scale = 0.85
        actions.append(f"mean_events high ({mean_e:.1f}) -> scale random *{scale}")
    elif mean_e < 3.5:
        scale = 1.18
        actions.append(f"mean_events low ({mean_e:.1f}) -> scale random *{scale}")
    else:
        actions.append(f"mean_events ok ({mean_e:.1f}) -> no global random scale")

    # Per-event rebalance: clamp outliers vs median
    counts = a["event_counts"]
    if counts:
        vals = list(counts.values())
        med = statistics.median(vals)
        hot = [e for e, c in counts.items() if c > med * 1.8]
        cold = [e for e, c in counts.items() if c < med * 0.45 and cluster_of(e) in HEAVY | {"cross"}]
        actions.append(f"hot={hot} cold={cold} median={med}")
    else:
        hot, cold = [], []
        med = 0

    if multi > a["runs"] * 0.25:
        actions.append("multi-heavy stacking high -> strengthen cross-cluster grudges -0.45->-0.55")

    if burst_pct < 30:
        actions.append("burst% low -> weaken sibling suppress -0.15,-0.55 -> -0.08,-0.45")
    elif burst_pct > 75:
        actions.append("burst% high -> strengthen sibling suppress")

    if dry_run:
        return actions

    # Apply file edits
    for path in EV_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        orig = text
        name_m = re.search(r"(?im)^Name\s*=\s*(\S+)", text)
        if not name_m:
            continue
        name = name_m.group(1).strip()

        def scale_random_line(m):
            lo, hi = float(m.group(2)), float(m.group(3))
            mid = (lo + hi) / 2
            half = (hi - lo) / 2 * scale
            # per-event nudge
            local = 1.0
            if name in hot:
                local = 0.82
            elif name in cold:
                local = 1.15
            # tech/health stay lighter
            if cluster_of(name) in {"tech_v2", "health_v2", "tech_v1", "health_v1"}:
                local *= 0.92
            elif cluster_of(name).startswith("climate") or cluster_of(name).startswith("housing") or cluster_of(name).startswith("mig"):
                local *= 1.05
            nlo = max(0.01, (mid - half) * local)
            nhi = min(0.40, (mid + half) * local)
            if nhi <= nlo:
                nhi = nlo + 0.02
            return f"{m.group(1)}_random_,{nlo:.3f},{nhi:.3f}"

        text = re.sub(
            r"(?m)^(\s*\d+\s*=\s*)_random_,([-\d.]+),([-\d.]+)",
            scale_random_line,
            text,
        )

        if multi > a["runs"] * 0.25:
            text = text.replace("CreateGrudge(HomelessCampCrisis,-0.45,0.80)", "CreateGrudge(HomelessCampCrisis,-0.55,0.82)")
            text = text.replace("CreateGrudge(LandlordExodus,-0.45,0.80)", "CreateGrudge(LandlordExodus,-0.55,0.82)")
            text = text.replace("CreateGrudge(CropFailureDrought,-0.45,0.80)", "CreateGrudge(CropFailureDrought,-0.55,0.82)")
            text = text.replace("CreateGrudge(CoastalFloodShock,-0.45,0.80)", "CreateGrudge(CoastalFloodShock,-0.55,0.82)")
            text = text.replace("CreateGrudge(ReceptionCenterRiot,-0.45,0.80)", "CreateGrudge(ReceptionCenterRiot,-0.55,0.82)")
            text = text.replace("CreateGrudge(SmugglerCorridorSpike,-0.45,0.80)", "CreateGrudge(SmugglerCorridorSpike,-0.55,0.82)")

        if burst_pct < 30:
            text = text.replace("CreateGrudge(CoastalFloodShock,-0.15,0.55)", "CreateGrudge(CoastalFloodShock,-0.08,0.45)")
            text = text.replace("CreateGrudge(CropFailureDrought,-0.15,0.55)", "CreateGrudge(CropFailureDrought,-0.08,0.45)")
            text = text.replace("CreateGrudge(LandlordExodus,-0.15,0.55)", "CreateGrudge(LandlordExodus,-0.08,0.45)")
            text = text.replace("CreateGrudge(HomelessCampCrisis,-0.15,0.55)", "CreateGrudge(HomelessCampCrisis,-0.08,0.45)")
            text = text.replace("CreateGrudge(SmugglerCorridorSpike,-0.15,0.55)", "CreateGrudge(SmugglerCorridorSpike,-0.08,0.45)")
            text = text.replace("CreateGrudge(ReceptionCenterRiot,-0.15,0.55)", "CreateGrudge(ReceptionCenterRiot,-0.08,0.45)")
        elif burst_pct > 75:
            text = text.replace("CreateGrudge(CoastalFloodShock,-0.15,0.55)", "CreateGrudge(CoastalFloodShock,-0.25,0.65)")
            text = text.replace("CreateGrudge(CropFailureDrought,-0.15,0.55)", "CreateGrudge(CropFailureDrought,-0.25,0.65)")
            text = text.replace("CreateGrudge(LandlordExodus,-0.15,0.55)", "CreateGrudge(LandlordExodus,-0.25,0.65)")
            text = text.replace("CreateGrudge(HomelessCampCrisis,-0.15,0.55)", "CreateGrudge(HomelessCampCrisis,-0.25,0.65)")
            text = text.replace("CreateGrudge(SmugglerCorridorSpike,-0.15,0.55)", "CreateGrudge(SmugglerCorridorSpike,-0.25,0.65)")
            text = text.replace("CreateGrudge(ReceptionCenterRiot,-0.15,0.55)", "CreateGrudge(ReceptionCenterRiot,-0.25,0.65)")

        if text != orig:
            path.write_text(text, encoding="utf-8", newline="\n")
            actions.append(f"patched {path.name}")
    return actions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--apply", action="store_true", help="write rebalance into event files")
    ap.add_argument("--rounds", type=int, default=1, help="analyze->apply loops")
    args = ap.parse_args()

    for rnd in range(args.rounds):
        print(f"\n######## ROUND {rnd + 1} ########")
        events = parse_events()
        rng = random.Random(args.seed + rnd * 997)
        results = [run_one(events, random.Random(rng.randint(1, 1_000_000_000))) for _ in range(args.runs)]
        a = analyze(results)
        print_report(a)
        if args.apply and rnd < args.rounds:
            actions = suggest_and_apply(a, dry_run=False)
            print("\n=== APPLY ===")
            for line in actions:
                print(line)
        else:
            actions = suggest_and_apply(a, dry_run=True)
            print("\n=== SUGGESTIONS (dry) ===")
            for line in actions:
                print(line)

    # final matrix CSV
    out = ROOT / "docs" / "superpowers" / "plans" / "balance-sim-50.md"
    events = parse_events()
    rng = random.Random(args.seed + 12345)
    results = [run_one(events, random.Random(rng.randint(1, 1_000_000_000))) for _ in range(args.runs)]
    a = analyze(results)
    lines = [
        "# Balance sim — Modern Pressure EU",
        "",
        f"Runs: {a['runs']} · seed base {args.seed}",
        f"Mean events/run: {a['mean_events']:.2f} · median {a['p50_events']:.1f}",
        f"Mean gap (turns): {a['mean_gap']}",
        f"Runs with burst pair ≤6 turns: {a['runs_with_burst_pct']:.1f}%",
        f"Multi-heavy same turn: {a['multi_heavy_same_turn']}",
        "",
        "## Cluster matrix",
        "",
        "| Cluster | Fires |",
        "|---------|------:|",
    ]
    for c, v in sorted(a["cluster_counts"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| {c} | {v} |")
    lines += ["", "## Event frequency", "", "| Event | Fires |", "|-------|------:|"]
    for e, v in a["event_counts"].most_common():
        lines.append(f"| {e} | {v} |")
    lines += ["", "## Top co-occurrence (same run)", "", "| A | B | Count |", "|---|---|------:|"]
    for (x, y), v in a["cooccurrence_top"]:
        lines.append(f"| {x} | {y} | {v} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
