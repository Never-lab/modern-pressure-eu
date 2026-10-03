# Modern Pressure EU — Design Spec (v2 Deepen)

**Date:** 2026-10-03  
**Game:** Democracy 4 (Steam Workshop)  
**Status:** Approved for planning (brainstorm lock)  
**Depends on:** `docs/superpowers/specs/2026-10-03-modern-pressure-eu-design.md` (v1)

## 1. Goal

Deepen the existing **Modern Pressure EU** pack on the same themes (climate, housing, tech/AI, migration, health). Same Workshop mod folder — no second mod. Add 20 policies and 12 crisis events with EU-felt weight (housing + climate + migration heavy; tech thin; health light), burst-style crisis pacing, and split intensity (priorities harsher than tech/health).

## 2. Locked decisions

| Decision | Choice |
|----------|--------|
| Approach | Same mod, additive deepen |
| Size | 20 new policies + 12 new events |
| Theme weight | Housing + climate + migration heavy; tech + health lighter |
| Crisis pacing | Burst: calm → cluster wave (often 2 close) → long cooldown |
| Intensity | Priorities one step above v1 retune; tech/health = v1 retune level |
| Gate | Vanilla `_prereq_eu` (no mission overrides) |
| Locales | Italian + English, identical keys |
| v1 IDs | Immutable; do not rename published policy/event Names |

## 3. Architecture

- Source: `ModernPressureEU/` at repo root.
- Load path: `%USERPROFILE%\Documents\My Games\Democracy4\mods\ModernPressureEU\`.
- Additive only: new `policies.csv` rows, new `data/simulation/events/*.txt`, IT/EN translation rows, SVG icons named `icons_<policyidlowercase>.svg`.
- No vanilla balance rewrites, no custom sim variables, no mission file copies.
- Validation: extend `tools/validate-mod.ps1` for full ID lists (v1+v2).
- Deploy: `tools/install-to-documents.ps1`.
- Update `config.txt` description to mention v2 deepen (IT-first guiname stays **Pressione Moderna UE**).

## 4. Totals after v2

| Content | v1 | v2 add | Total |
|---------|----|--------|-------|
| Policies | 12 | 20 | 32 |
| Events | 8 | 12 | 20 |

## 5. Policy inventory (v2) — exact IDs

### Climate / energy (6) — priority intensity

| ID | EN GUI name | Role |
|----|-------------|------|
| `HeatPumpMandate` | Heat Pump Mandate | Capex mandate; energy/industry friction |
| `AgriMethaneCap` | Agri Methane Cap | Farmers vs environment |
| `IndustrialElectrificationFund` | Industrial Electrification Fund | Debt/GDP vs CO2 cut |
| `DroughtWaterRationing` | Drought Water Rationing | Popularity vs agriculture/tourism |
| `CoastalDefenseLevy` | Coastal Defense Levy | Ongoing cost vs climate risk |
| `NuclearLifeExtension` | Nuclear Life Extension | Energy up; green/NIMBY tension |

### Housing / cost of living (6) — priority intensity

| ID | EN GUI name | Role |
|----|-------------|------|
| `VacancyTax` | Vacancy Tax | Empty homes; landlords angry |
| `ShortTermRentalCap` | Short-Term Rental Cap | Tourism income vs housing supply |
| `FirstHomeGuarantee` | First-Home Guarantee | Middle class up; debt pressure |
| `LandlordEnergyUpgradeDuty` | Landlord Energy Upgrade Duty | Efficiency up; landlord fury |
| `AntiEvictionMoratorium` | Anti-Eviction Moratorium | Poor up; capitalist hard down |
| `UrbanDensificationAct` | Urban Densification Act | Supply relief; NIMBY backlash |

### Migration (5) — priority intensity

| ID | EN GUI name | Role |
|----|-------------|------|
| `ExternalAsylumHubs` | External Asylum Hubs | Right-leaning relief; liberal/foreign-relations cost |
| `LocalReceptionQuota` | Local Reception Quota | Territorial tension |
| `LabourInspectionBlitz` | Labour Inspection Blitz | Illegal work down; business friction |
| `CitizenshipTrackReform` | Citizenship Track Reform | Integration path; culture clash |
| `SchengenFlexControls` | Schengen Flex Controls | Security vs EU relations |

### Tech (1) — v1 intensity

| ID | EN GUI name | Role |
|----|-------------|------|
| `AlgorithmicPublicServices` | Algorithmic Public Services | Efficiency vs trust/privacy |

### Health (2) — v1 intensity

| ID | EN GUI name | Role |
|----|-------------|------|
| `MentalHealthAccessAct` | Mental Health Access Act | Popular; expensive |
| `ElderCareInsurance` | Elder Care Insurance | Parents/elderly up; debt |

### Policy design rules (v2)

- All gated by `_prereq_eu`.
- Each policy: meaningful cost + at least one painful side effect.
- Priority themes: larger effect magnitudes and clearer voter polarisation than v1 retune.
- Tech/health: match v1 post-retune magnitude band.
- Inertia on major effects: prefer 3–6 (readable pressure; not molasses).
- Effects target existing simulation objects only.
- Icons: copy closest vanilla SVG into `data/svg/icons_<idlowercase>.svg`.
- Departments: follow vanilla department enums already used in v1 (`ECONOMY`, `WELFARE`, `PUBLICSERVICES`, `FOREIGNPOLICY`, `LAWANDORDER`).

## 6. Event inventory (v2) — exact Names

### Climate cluster (burst pair)

| Name | EN title |
|------|----------|
| `CropFailureDrought` | Crop Failure Drought |
| `CoastalFloodShock` | Coastal Flood Shock |

### Housing cluster (burst pair)

| Name | EN title |
|------|----------|
| `HomelessCampCrisis` | Homeless Camp Crisis |
| `LandlordExodus` | Landlord Exodus |

### Migration cluster (burst pair)

| Name | EN title |
|------|----------|
| `ReceptionCenterRiot` | Reception Center Riot |
| `SmugglerCorridorSpike` | Smuggler Corridor Spike |

### Tech cluster (lighter, no aggressive burst)

| Name | EN title |
|------|----------|
| `PublicDataLeak` | Public Data Leak |
| `AutomationStrike` | Automation Strike |

### Health cluster (lighter)

| Name | EN title |
|------|----------|
| `AmbulanceGridlock` | Ambulance Gridlock |
| `CareHomeOutbreak` | Care Home Outbreak |

### Cross pressure

| Name | EN title |
|------|----------|
| `CostOfLivingMarch` | Cost of Living March |
| `EUFiscalWarning` | EU Fiscal Warning |

### Burst / exclusion rules

1. **Heavy clusters** (climate, housing, migration): after one fires, sibling influence boosted for ~2–4 turns, then long `CreateGrudge` on both Names.
2. **Cross-cluster soft exclusion:** while any heavy-cluster event is active/on short cooldown, other heavy clusters have sharply reduced chance (avoid triple waves).
3. **Tech/health:** lower base chance; sibling suppression only (no boost window).
4. **v1 events:** keep existing mutual-exclusion pairs; add soft links so v2 housing/climate/migration waves do not stack on top of active v1 siblings of the same theme when cheap to wire.
5. **Target feel:** calm stretch → often a 2-event cluster wave → long quiet. Not 1 crisis every turn.

Event files: same shape as v1 (prereq influence `_prereq_,_prereq_eu`, texture/sound reuse from vanilla, EN+IT rows in `translations/*/events.csv`).

## 7. Localization

- Every new policy: GUI name + description in `translations/English/policies.csv` and `translations/Italian/policies.csv`.
- Every new event: title + description in both `events.csv` files.
- Italian copy: short, punchy, tradeoff-clear (match v1 retune style).

## 8. Tooling updates

- `tools/validate-mod.ps1`: assert all 32 policy IDs and 20 event Names; each gated with `_prereq_eu`; EN/IT key parity.
- `tools/install-to-documents.ps1`: unchanged flow; always redeploy after content commits.
- Optional: bump description string in install script to mention deepen/burst.

## 9. Acceptance criteria (v2 done)

1. Mods panel still lists **Pressione Moderna UE**; description mentions deepened content.
2. On EU mission (Italy): all 32 policies available under normal unlock rules; IT/EN strings present.
3. On non-EU (USA/UK): zero mod policies; zero mod events.
4. Long EU run: at least one heavy-cluster burst (two related events close together) can occur; no softlock/crash through turn 30.
5. `validate-mod.ps1` passes at repo root.
6. Workshop upload remains manual in-game step.

## 10. Non-goals (v2)

- Separate expansion mod or Workshop dependency chain.
- New playable countries.
- New custom simulation variables / prereqs beyond `_prereq_eu`.
- Full SVG art pass / custom audio.
- Locales beyond IT+EN.
- Rewriting vanilla global balance CSVs.
- Renaming or removing v1 content.

## 11. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Crisis spam from +12 events | Burst grudges + cross-cluster soft exclusion; conservative bases first |
| ID collision with other mods | Unique CamelCase Names; spot-check against install |
| Impossible one-shot tuning | Ship conservative; playtest retune commit after |
| Invalid effect targets crash | Reuse only targets proven in v1 or present in vanilla CSVs |
| Scope creep mid-build | Inventory above is authoritative; no extra IDs without spec amend |

## 12. Review history

- Brainstorm 2026-10-03: deepen A–E → size C (~15–20 / 10+) → weight housing/climate/migration → burst crises → intensity split → approach same-mod additive → 20 policies + 12 events inventories approved section-by-section.
- Spec self-review: policy count was 21 with both tech IDs; dropped `OpenSourceGovStack` to hit exact 20 (clima 6 / casa 6 / migrazione 5 / tech 1 / sanità 2).
