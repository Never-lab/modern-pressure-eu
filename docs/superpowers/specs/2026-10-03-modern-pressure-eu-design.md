# Modern Pressure EU — Design Spec (v1 MVP)

**Date:** 2026-10-03  
**Game:** Democracy 4 (Steam Workshop)  
**Status:** Draft for user review (post 10-loop plan review)

## 1. Goal

Ship a **modern pressure content pack** for Democracy 4: new policies + crisis events themed around climate, housing, tech/AI, migration, and health. Difficulty is **hardcore A+/B−** (high costs, slow recovery, crises present but not pure chaos). Target playable **EU missions only** via a custom prerequisite flag.

This is **not** a vanilla economy rewrite. Workshop description must call it a *pressure pack*, not a full overhaul.

## 2. Approach (locked)

**Approach 1+ (additive + EU flag):**

- Add new `policies.csv` rows and event `.txt` files only (no wholesale vanilla CSV rewrites).
- **F1 exception:** for each v1 EU mission, add a minimal mission override that sets `_prereq_mod_eu = 1`.
- Declare `_prereq_mod_eu` in mod `data/simulation/prereqs.txt`.
- All new policies/events require `_prereq_mod_eu` (or equivalent column usage) so they do not appear / fire on non-EU missions.

## 3. Dev & install paths

| Role | Path |
|------|------|
| Source of truth (this repo) | `ModernPressureEU/` at workspace root |
| In-game load (Windows) | `%USERPROFILE%\Documents\My Games\Democracy4\mods\ModernPressureEU\` |
| Workshop upload | In-game Mods panel after local test passes |

`config.txt` `path` must match the Documents mods folder on the author’s machine (update if username/path differs).

## 4. Folder layout

```
ModernPressureEU/
  config.txt
  data/
    simulation/
      policies.csv
      prereqs.txt
      # Event files: same relative paths/names as vanilla Democracy 4
    # (discovered from install at implementation; content IDs below are authoritative)
    missions/
      germany/overrides/   # + france, italy, greece, ireland, poland as present
    svg/                   # only if vanilla icon reuse is impossible
  translations/
    english/
      policies.csv
      # plus event string files mirroring vanilla layout
    italian/
      policies.csv
```

Event **content IDs** (section 7) are fixed; on-disk filenames follow whatever layout the local Democracy 4 install uses for simulation events.

## 5. EU mission set (v1)

Set `_prereq_mod_eu = 1` only on these playable missions (folder names confirmed against install at implement time):

| Mission (expected) | EU v1 |
|--------------------|-------|
| Germany | yes |
| France | yes |
| Italy | yes |
| Greece | yes (if present / DLC) |
| Ireland | yes (if present / DLC) |
| Poland | yes (if present / DLC) |
| United Kingdom | **no** (not EU) |
| Switzerland | **no** |
| Turkey | **no** |
| USA, Canada, Brazil, others | **no** |

If a listed EU mission is missing from the install, skip it; do not fail the whole mod. If folder IDs differ (e.g. `germany` vs `Germany`), use the on-disk mission id.

## 6. Policy inventory (12)

Coverage: **thin across A–E** (2–3 each). IDs are stable; do not rename after Workshop publish without a migration note.

| # | ID | Theme | GUI name (EN) | Role (hardcore) |
|---|----|-------|---------------|-----------------|
| 1 | `CarbonBorderAdjustment` | A Climate | Carbon Border Adjustment | Costly trade friction; helps environment / industry tension |
| 2 | `GridStorageMandate` | A Climate | Grid Storage Mandate | Capex-heavy resilience; reduces blackout risk slowly |
| 3 | `RenovationWaveSubsidies` | A Climate | Renovation Wave Subsidies | Expensive; housing quality + emissions, slow inertia |
| 4 | `RentStabilizationAct` | B Housing | Rent Stabilization Act | Voters love short-term; investment/housing supply pain |
| 5 | `SocialHousingSurge` | B Housing | Social Housing Surge | Very expensive; slow relief to homelessness/housing |
| 6 | `AIWorkplaceAudit` | C Tech | AI Workplace Audit | Softens layoff backlash; costs business / tech growth |
| 7 | `PublicComputeCloud` | C Tech | Public Compute Cloud | Capex + tech; debt pressure; long inertia |
| 8 | `PlatformDutyOfCare` | C Tech | Platform Duty of Care | Privacy/trust up; GDP/tech friction |
| 9 | `AsylumProcessingSurge` | D Migration | Asylum Processing Surge | Costly capacity; reduces border-crisis severity |
| 10 | `SkillsVisaFastTrack` | D Migration | Skills Visa Fast Track | Growth/labour relief; cultural/immigration tension |
| 11 | `SurgicalWaitCap` | E Health | Surgical Wait Cap | Popular + expensive; strained health budget |
| 12 | `PandemicStockpileLaw` | E Health | Pandemic Stockpile Law | Ongoing cost; dampens health-crisis events |

### Policy design rules

- Each policy: meaningful **cost** (budget and/or GDP drag) and **at least one painful side effect**.
- Inertia on major effects: prefer **4–8** (slow recovery / slow payoff) to match A+/B−.
- All policies gated by `_prereq_mod_eu`.
- Effects target existing simulation objects only (no new custom sims in v1) unless implementation discovers a trivial safe extension; prefer vanilla stats/groups (`Environment`, `GDP`, `Debt`, `Homelessness`, `Technology`, `Health`, `Immigration`, voter groups, etc.).
- Icons v1: reuse closest vanilla SVG references if the pipeline allows; otherwise ship minimal placeholder SVGs named `icons_<policyid>.svg`.

## 7. Event inventory (8)

| # | ID | Theme | EN title | Pressure |
|---|----|-------|----------|----------|
| 1 | `HeatGridFailure` | A | Heatwave Grid Failure | Energy/environment crisis; hurts poor + economy |
| 2 | `EnergyPriceSpike` | A | Energy Price Spike | Cost of living spike; industry anger |
| 3 | `RentStrikeWave` | B | Rent Strike Wave | Housing unrest; liberals/poor vs landlords/investors |
| 4 | `MortgageStress` | B | Mortgage Stress Wave | Middle-class hit; GDP/debt stress |
| 5 | `AILayoffBacklash` | C | AI Layoff Backlash | Unemployment + tech backlash |
| 6 | `DeepfakeScandal` | C | Deepfake Scandal | Trust/political capital hit |
| 7 | `BorderProcessingCollapse` | D | Border Processing Collapse | Immigration flashpoint |
| 8 | `HospitalWinterCrisis` | E | Hospital Winter Crisis | Health system overload |

### Event budget (locked)

- Require `_prereq_mod_eu`.
- **Mutual exclusion by theme pair:** while a theme’s “heavy” event is active/on cooldown, its pair sibling has sharply reduced chance (A1↔A2, B3↔B4, C5↔C6).
- Target feel: roughly **one serious crisis every 8–12 turns** on typical play, not stacked multi-theme pileups every turn.
- Each event offers **costly mitigation** options where the format supports choices; “ignore” is worse medium-term.
- Tuning constants live in event files; document final chance values in the implementation plan after reading vanilla event syntax from the install.

## 8. Localization

- `translations/english` and `translations/italian` with **identical keys**.
- Every policy GUI name + description in both languages.
- Every player-facing event string in both languages.
- Folder casing must match base game (`english` / `italian` verified on install).

## 9. `config.txt` (authoring template)

```ini
[config]
name = ModernPressureEU
path = C:\Users\nicho\Documents\My Games\Democracy4\mods\ModernPressureEU
guiname = Modern Pressure EU
author = nicho
description = EU pressure pack: climate, housing, tech/AI, migration, health. Hard costs, slow payoffs, serious crises. Additive content + EU mission flag. Not a full economy overhaul.
```

## 10. Acceptance criteria (v1 done)

1. Mod appears in Democracy 4 Mods panel with correct name/description.
2. On an **EU** mission (e.g. France or Germany): all 12 policies are available (or unlockable per normal rules) and show EN or IT text when that language is selected.
3. On a **non-EU** mission (e.g. USA or UK): none of the 12 policies appear; none of the 8 events fire.
4. Fresh EU run to **turn 20**: no crash/softlock; at least one mod event can be observed in a longer stress run or via elevated test chances in a private test build (production chances stay on budget).
5. Workshop-ready folder structure; upload is a manual in-game step (out of repo automation scope).

## 11. Non-goals (v1)

- Rewriting vanilla `policies.csv` balance for all policies.
- New playable countries.
- New simulation variables beyond a single custom prereq.
- Full SVG art pass / audio.
- Non-EU localization beyond IT+EN.

## 12. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| EU flag not applied (policies global) | Acceptance #3; checklist of mission overrides |
| Event spam feels Brutal (B) | Event budget + mutual exclusion |
| CSV format break | Edit as UTF-8 CSV; lines start with `#`; validate against vanilla row shape |
| Missing DLC missions | Skip absent folders |
| ID collision with other mods | Prefer unique prefixed IDs if collisions found at test (`MPE_` prefix fallback) |

## 13. Review history

- Brainstorming: overhaul → modern+hardcore → MVP A → themes A–E thin → IT+EN → hardcore A+/B− → EU bloc → approach 1.
- 10-loop thrifty plan review: Critical UE/prereq + inventory closed by F1 + this inventory; Important event budget, acceptance, icons, Documents path locked above.
- User confirmation: proceed with F1, author-owned inventory, and locked Important items.
