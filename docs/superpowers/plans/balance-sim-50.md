# Balance sim — Modern Pressure EU

Proxy Monte Carlo (not the real D4 engine): 50 runs x 60 turns, event eval every 3 turns, `_prereq_eu` as gate.

## Targets vs result (seed 123)

| Metric | Target | Result |
|--------|--------|--------|
| Mean events / run | 6–10 | **9.5** |
| Burst pair within 6 turns | 35–60% runs | **48%** |
| Multi-heavy same turn | ~0 | **0** |
| Heavy > light clusters | yes | climate/housing/mig dominate; tech_v2/health_v2 rare |

## Cluster matrix (fires across 50 runs)

| Cluster | Fires |
|---------|------:|
| climate_v1 | 120 |
| housing_v2 | 96 |
| mig_v2 | 58 |
| tech_v1 | 46 |
| health_v1 | 40 |
| housing_v1 | 39 |
| climate_v2 | 35 |
| mig_v1 | 25 |
| cross | 16 |

## Changes applied

- Event `_random_` bands retuned; heavy v2 drivers strengthened; sibling burst grudges softened then re-tightened
- Policy costs: + on cheap tech soft-reg; - slight on mega-capex outliers
- Tooling: `tools/simulate-balance.py`

## How to re-run

```powershell
python tools/simulate-balance.py --runs 50 --seed 123
```
