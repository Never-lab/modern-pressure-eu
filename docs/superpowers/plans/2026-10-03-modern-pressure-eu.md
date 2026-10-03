# Modern Pressure EU Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the Democracy 4 additive mod `ModernPressureEU` (12 EU-gated policies, 8 crisis events, IT+EN) per `docs/superpowers/specs/2026-10-03-modern-pressure-eu-design.md`.

**Architecture:** Mirror vanilla folder layout under `ModernPressureEU/`. Declare `_prereq_mod_eu` in `prereqs.txt`. Inject `_prereq_mod_eu = 1` into each present EU mission’s country `[policies]` block (F1). Gate all new policies/events on that prereq. Validate with a PowerShell checker; playtest in-game from Documents mods path.

**Tech Stack:** Democracy 4 data files (CSV + INI-like `.txt`), UTF-8 text, PowerShell validation, Steam Workshop upload via in-game UI.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-10-03-modern-pressure-eu-design.md` (authoritative inventory and acceptance).
- Additive only: do not rewrite vanilla global balance CSVs; only new rows/files + EU mission prereq injection.
- Policy IDs (exact): `CarbonBorderAdjustment`, `GridStorageMandate`, `RenovationWaveSubsidies`, `RentStabilizationAct`, `SocialHousingSurge`, `AIWorkplaceAudit`, `PublicComputeCloud`, `PlatformDutyOfCare`, `AsylumProcessingSurge`, `SkillsVisaFastTrack`, `SurgicalWaitCap`, `PandemicStockpileLaw`.
- Event Names (exact): `HeatGridFailure`, `EnergyPriceSpike`, `RentStrikeWave`, `MortgageStress`, `AILayoffBacklash`, `DeepfakeScandal`, `BorderProcessingCollapse`, `HospitalWinterCrisis`.
- Prereq name (exact): `_prereq_mod_eu`.
- EU missions to flag if present: `germany`, `france`, `italy`, `greece`, `ireland`, `poland` (confirm on-disk folder names in Task 1).
- Non-EU must stay ungated: UK, Switzerland, Turkey, USA, Canada, Brazil, others.
- Locales: `translations/english` + `translations/italian`, identical keys.
- Hardcore A+/B−: high costs, inertia 4–8 on major effects, event budget ~one serious crisis / 8–12 turns, mutual exclusion within theme pairs.
- Dev source: `ModernPressureEU/` at repo root; load path: `C:\Users\nicho\Documents\My Games\Democracy4\mods\ModernPressureEU`.
- All CSV object rows must start with `#` in column A; save UTF-8 CSV (not Excel XML).

---

## File map

| Path | Responsibility |
|------|----------------|
| `ModernPressureEU/config.txt` | Mod metadata for in-game panel |
| `ModernPressureEU/data/simulation/prereqs.txt` | Declares `_prereq_mod_eu` |
| `ModernPressureEU/data/simulation/policies.csv` | 12 new policies |
| `ModernPressureEU/data/simulation/events/*.txt` | 8 events (filenames from vanilla convention) |
| `ModernPressureEU/data/missions/<eu>/*.txt` | Vanilla mission copy + `_prereq_mod_eu = 1` |
| `ModernPressureEU/translations/english/policies.csv` | EN GUI strings |
| `ModernPressureEU/translations/italian/policies.csv` | IT GUI strings |
| `ModernPressureEU/translations/*/events.csv` or per-file strings | Event text (match vanilla layout from Task 1) |
| `tools/validate-mod.ps1` | Structural acceptance checks |
| `reference/` | Copied vanilla samples (not shipped in Workshop zip if undesired; keep in repo) |

---

### Task 1: Locate install + capture vanilla references

**Files:**
- Create: `reference/README.md`
- Create: `reference/policies.header.csv` (first 2 lines of vanilla policies.csv)
- Create: `reference/sample_policy_row.csv` (one complete `#` policy row)
- Create: `reference/prereqs.txt` (copy of vanilla)
- Create: `reference/sample_event.txt` (one vanilla event)
- Create: `reference/sample_mission.txt` (one EU mission country file, e.g. france)
- Create: `reference/translation_policies.header.csv`
- Create: `reference/missions_list.txt` (folder names under `data/missions`)
- Create: `reference/events_locale_note.md` (where event strings live)

**Interfaces:**
- Consumes: local Democracy 4 Steam/GOG install
- Produces: exact column order, event file shape, mission ids, translation file layout for later tasks

- [ ] **Step 1: Find the game install**

```powershell
$roots = @(
  "C:\Program Files (x86)\Steam\steamapps\common\Democracy 4",
  "C:\Program Files\Steam\steamapps\common\Democracy 4",
  "D:\SteamLibrary\steamapps\common\Democracy 4",
  "E:\SteamLibrary\steamapps\common\Democracy 4"
)
$game = $roots | Where-Object { Test-Path (Join-Path $_ "data\simulation\policies.csv") } | Select-Object -First 1
if (-not $game) { throw "Democracy 4 not found. Ask user for install path." }
$game | Set-Content -Encoding utf8 "reference/game_path.txt"
Write-Output "GAME=$game"
```

Expected: `GAME=` path printed; `reference/game_path.txt` exists. If throw → stop plan, ask user for path, resume Task 1.

- [ ] **Step 2: Copy reference artifacts**

```powershell
$game = Get-Content "reference/game_path.txt" -Raw
$game = $game.Trim()
New-Item -ItemType Directory -Force -Path reference | Out-Null
Get-ChildItem (Join-Path $game "data\missions") -Directory | ForEach-Object { $_.Name } |
  Set-Content -Encoding utf8 "reference/missions_list.txt"
$pol = Join-Path $game "data\simulation\policies.csv"
Get-Content $pol -TotalCount 2 | Set-Content -Encoding utf8 "reference/policies.header.csv"
Get-Content $pol | Where-Object { $_ -match '^#' } | Select-Object -First 1 |
  Set-Content -Encoding utf8 "reference/sample_policy_row.csv"
Copy-Item (Join-Path $game "data\simulation\prereqs.txt") "reference/prereqs.txt"
$evDir = Join-Path $game "data\simulation\events"
$sampleEv = Get-ChildItem $evDir -Filter *.txt | Select-Object -First 1
Copy-Item $sampleEv.FullName "reference/sample_event.txt"
# pick first existing EU-ish mission for sample
$euGuess = @("france","germany","italy","France","Germany","Italy")
$mission = $null
foreach ($e in $euGuess) {
  $p = Join-Path $game "data\missions\$e"
  if (Test-Path $p) { $mission = $e; break }
}
if (-not $mission) { throw "No france/germany/italy mission folder found" }
$missionTxt = Get-ChildItem (Join-Path $game "data\missions\$mission") -Filter *.txt | Select-Object -First 1
Copy-Item $missionTxt.FullName "reference/sample_mission.txt"
$mission | Set-Content -Encoding utf8 "reference/sample_mission_id.txt"
# translations
$tr = Join-Path $game "translations"
Get-ChildItem $tr -Directory | ForEach-Object { $_.Name } | Set-Content -Encoding utf8 "reference/translation_folders.txt"
$enPol = Join-Path $tr "english\policies.csv"
if (-not (Test-Path $enPol)) { $enPol = Get-ChildItem $tr -Recurse -Filter policies.csv | Select-Object -First 1 -ExpandProperty FullName }
Get-Content $enPol -TotalCount 2 | Set-Content -Encoding utf8 "reference/translation_policies.header.csv"
Get-Content $enPol | Where-Object { $_ -match '^#' } | Select-Object -First 1 |
  Set-Content -Encoding utf8 "reference/sample_translation_policy_row.csv"
# note event string location
@"
Inspected events dir: $evDir
Translation root: $tr
Document here after manual open: whether event text is inside each event .txt, or in translations/*/events.csv (or similar).
"@ | Set-Content -Encoding utf8 "reference/events_locale_note.md"
```

- [ ] **Step 3: Write `reference/README.md`**

```markdown
# Vanilla reference snapshots

Captured from the local Democracy 4 install listed in `game_path.txt`.
Later tasks MUST match column order in `policies.header.csv` and mission/event shapes in the sample files.
Do not ship `reference/` to Workshop (keep in git only).
```

- [ ] **Step 4: Verify references exist**

```powershell
@(
  "reference/game_path.txt",
  "reference/policies.header.csv",
  "reference/sample_policy_row.csv",
  "reference/prereqs.txt",
  "reference/sample_event.txt",
  "reference/sample_mission.txt",
  "reference/missions_list.txt",
  "reference/translation_policies.header.csv"
) | ForEach-Object { if (-not (Test-Path $_)) { throw "missing $_" } else { $_ } }
```

Expected: each path printed; no throw.

- [ ] **Step 5: Commit**

```bash
git init  # only if repo not already initialized
git add reference docs/superpowers
git commit -m "chore: capture Democracy 4 vanilla references for Modern Pressure EU"
```

---

### Task 2: Scaffold mod + config + prereq declaration

**Files:**
- Create: `ModernPressureEU/config.txt`
- Create: `ModernPressureEU/data/simulation/prereqs.txt`
- Create: `ModernPressureEU/data/simulation/policies.csv` (header-only stub)
- Create: `ModernPressureEU/translations/english/policies.csv` (header stub)
- Create: `ModernPressureEU/translations/italian/policies.csv` (header stub)

**Interfaces:**
- Consumes: `reference/policies.header.csv`, `reference/translation_policies.header.csv`, `reference/prereqs.txt` format
- Produces: loadable empty mod shell with `_prereq_mod_eu` declared

- [ ] **Step 1: Create directories**

```powershell
$dirs = @(
  "ModernPressureEU/data/simulation/events",
  "ModernPressureEU/data/missions",
  "ModernPressureEU/translations/english",
  "ModernPressureEU/translations/italian",
  "ModernPressureEU/data/svg",
  "ModernPressureEU/data/bitmaps"
)
$dirs | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }
```

- [ ] **Step 2: Write `ModernPressureEU/config.txt`**

```ini
[config]
name = ModernPressureEU
path = C:\Users\nicho\Documents\My Games\Democracy4\mods\ModernPressureEU
guiname = Modern Pressure EU
author = nicho
description = EU pressure pack: climate, housing, tech/AI, migration, health. Hard costs, slow payoffs, serious crises. Additive content + EU mission flag. Not a full economy overhaul.
```

- [ ] **Step 3: Write `ModernPressureEU/data/simulation/prereqs.txt`**

Match vanilla numbering style from `reference/prereqs.txt`. Append a new index after the last vanilla index. Example shape (adjust index `N` to `last+1` from reference):

```txt
N = _prereq_mod_eu
```

If vanilla uses only names without indices, copy that style exactly and add `_prereq_mod_eu` alone on a new line.

- [ ] **Step 4: Copy CSV headers into stub policies/translation files**

```powershell
Get-Content "reference/policies.header.csv" -TotalCount 1 |
  Set-Content -Encoding utf8 "ModernPressureEU/data/simulation/policies.csv"
"# Modern Pressure EU policies follow" |
  Add-Content -Encoding utf8 "ModernPressureEU/data/simulation/policies.csv"
Get-Content "reference/translation_policies.header.csv" -TotalCount 1 |
  Set-Content -Encoding utf8 "ModernPressureEU/translations/english/policies.csv"
Get-Content "reference/translation_policies.header.csv" -TotalCount 1 |
  Set-Content -Encoding utf8 "ModernPressureEU/translations/italian/policies.csv"
```

- [ ] **Step 5: Commit**

```bash
git add ModernPressureEU
git commit -m "feat: scaffold ModernPressureEU mod shell and EU prereq"
```

---

### Task 3: Inject `_prereq_mod_eu` into EU missions (F1)

**Files:**
- Create: `tools/inject-eu-prereq.ps1`
- Create: `ModernPressureEU/data/missions/<id>/<id>.txt` for each present EU mission

**Interfaces:**
- Consumes: `reference/game_path.txt`, `reference/sample_mission.txt`, mission folder names
- Produces: mission files that set `_prereq_mod_eu = 1` under `[policies]`

- [ ] **Step 1: Write injector script `tools/inject-eu-prereq.ps1`**

```powershell
param(
  [string]$GamePath = (Get-Content "reference/game_path.txt" -Raw).Trim(),
  [string]$ModRoot = "ModernPressureEU",
  [string[]]$EuIds = @("germany","france","italy","greece","ireland","poland")
)
$ErrorActionPreference = "Stop"
$missionsRoot = Join-Path $GamePath "data\missions"
$found = @()
foreach ($id in $EuIds) {
  $match = Get-ChildItem $missionsRoot -Directory | Where-Object { $_.Name -ieq $id } | Select-Object -First 1
  if (-not $match) { Write-Warning "Skip missing mission $id"; continue }
  $srcTxt = Get-ChildItem $match.FullName -Filter "*.txt" | Where-Object { $_.BaseName -ieq $match.Name } | Select-Object -First 1
  if (-not $srcTxt) { $srcTxt = Get-ChildItem $match.FullName -Filter "*.txt" | Select-Object -First 1 }
  if (-not $srcTxt) { throw "No txt in $($match.FullName)" }
  $destDir = Join-Path $ModRoot "data\missions\$($match.Name)"
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null
  $dest = Join-Path $destDir $srcTxt.Name
  $text = Get-Content $srcTxt.FullName -Raw
  if ($text -notmatch '(?im)^_prereq_mod_eu\s*=') {
    if ($text -notmatch '(?im)\[policies\]') { throw "$($match.Name) missing [policies] section" }
    $text = [regex]::Replace($text, '(?im)(\[policies\]\s*)', "`$1`r`n_prereq_mod_eu = 1`r`n", 1)
  }
  Set-Content -Path $dest -Value $text -Encoding utf8
  $found += $match.Name
}
if ($found.Count -lt 1) { throw "No EU missions injected" }
"Injected: $($found -join ', ')" | Set-Content -Encoding utf8 "reference/eu_missions_injected.txt"
Write-Output "Injected: $($found -join ', ')"
```

- [ ] **Step 2: Run injector**

```powershell
powershell -NoProfile -File tools/inject-eu-prereq.ps1
```

Expected: `Injected: ...` including at least `france` or `germany` or `italy`.

- [ ] **Step 3: Verify line present**

```powershell
Get-ChildItem "ModernPressureEU/data/missions" -Recurse -Filter *.txt | ForEach-Object {
  if ((Get-Content $_.FullName -Raw) -notmatch '(?im)^_prereq_mod_eu\s*=\s*1') { throw "missing prereq in $($_.FullName)" }
  $_.FullName
}
```

Expected: each injected mission path printed; no throw.

- [ ] **Step 4: Commit**

```bash
git add tools/inject-eu-prereq.ps1 ModernPressureEU/data/missions reference/eu_missions_injected.txt
git commit -m "feat: inject _prereq_mod_eu into EU Democracy 4 missions"
```

---

### Task 4: Add 12 policies + EN/IT policy strings

**Files:**
- Modify: `ModernPressureEU/data/simulation/policies.csv`
- Modify: `ModernPressureEU/translations/english/policies.csv`
- Modify: `ModernPressureEU/translations/italian/policies.csv`

**Interfaces:**
- Consumes: exact column order from `reference/policies.header.csv` and `reference/sample_policy_row.csv`
- Produces: 12 `#` policy rows, each with PreReqs containing `_prereq_mod_eu`, hardcore costs, inertia 4–8, ≥1 painful side effect

- [ ] **Step 1: Map columns from the sample row**

Open `reference/policies.header.csv` + `reference/sample_policy_row.csv`. Build a mental map of indices for: Name, Slider, Flags, Opposites, Introduce, Cancel, Raise, Lower, Department, PreReqs, MinCost, MaxCost, CostFunction, Cost Multiplier, Implementation, MinIncome, MaxIncome, IncomeFunction, Income Multiplier, nationalisation, `#Effects`, then effect cells.

- [ ] **Step 2: Append all 12 policy rows**

Use Slider=`default`, blank Flags/Opposites unless needed, high Introduce costs (e.g. 8–14), PreReqs=`_prereq_mod_eu`, CostFunction=`0+(1.0*x)`, Income mostly `0`, Implementation `3`–`6`.  
Departments (pick valid vanilla department tokens from sample rows / nearby policies): Climate/energy → economy/environment-adjacent; Housing → welfare; Tech → economy; Migration → foreign/law; Health → public services — **copy exact department strings from vanilla rows of similar policies**, do not invent tokens.

**Balance targets (apply in effect cells; tune numbers to vanilla magnitude from sample):**

| ID | MinCost–MaxCost (order of magnitude) | Main + effects | Pain side effects |
|----|--------------------------------------|----------------|-------------------|
| CarbonBorderAdjustment | mid-high | Environment↑, InternationalTrade tension | GDP↓, ForeignRelations↓ or capitalist anger |
| GridStorageMandate | high | Energy resilience / Environment↑ | Debt↑ or GDP↓ |
| RenovationWaveSubsidies | high | Environment↑, Homelessness slight↓ | Debt↑, slow inertia 6–8 |
| RentStabilizationAct | mid | Poor/Socialist↑, Homelessness↓ | Capitalism/GDP↓, housing investment pain |
| SocialHousingSurge | very high | Homelessness↓, Poor↑ | Debt↑↑, Tax↑ pressure |
| AIWorkplaceAudit | mid | Unemployment slight↓, Liberal↑ | Technology↓, Capitalism↓ |
| PublicComputeCloud | very high | Technology↑ | Debt↑↑, Tax |
| PlatformDutyOfCare | mid | Liberal/Privacy-ish↑ | Technology↓, GDP slight↓ |
| AsylumProcessingSurge | high | Immigration situation relief | Debt↑, Conservative↓ |
| SkillsVisaFastTrack | mid | GDP/Technology↑, labour relief | Immigration tension / Conservative↓ |
| SurgicalWaitCap | high | Health↑, Parents/Everyone↑ | Debt↑ |
| PandemicStockpileLaw | mid ongoing | Health resilience | Debt↑ |

Each effect cell format: `Target,0.0+(0.0*x),Inertia` with Inertia 4–8. Include self-identity effects only if vanilla patterns do.

Write the full CSV rows into `policies.csv` (header already present). Every data row starts with `#`.

- [ ] **Step 3: Write EN translations**

Match `reference/translation_policies.header.csv` / sample row shape. Typical pattern:

```csv
#,CarbonBorderAdjustment,Carbon Border Adjustment,"Imposes carbon costs on imports. Helps climate goals but raises prices and trade friction."
#,GridStorageMandate,Grid Storage Mandate,"Forces large-scale electricity storage. Expensive resilience against blackouts."
#,RenovationWaveSubsidies,Renovation Wave Subsidies,"Subsidises deep building renovations. Slow climate and housing-quality gains at high fiscal cost."
#,RentStabilizationAct,Rent Stabilization Act,"Caps rent growth. Popular with tenants; deters housing investment."
#,SocialHousingSurge,Social Housing Surge,"Mass public housebuilding. Heavy budget cost; slow relief for homelessness."
#,AIWorkplaceAudit,AI Workplace Audit,"Regulates automated layoffs. Softens backlash; slows tech adoption."
#,PublicComputeCloud,Public Compute Cloud,"State compute infrastructure. Long-run tech capacity; serious debt pressure."
#,PlatformDutyOfCare,Platform Duty of Care,"Holds platforms liable for harms. Trust gains; business and tech friction."
#,AsylumProcessingSurge,Asylum Processing Surge,"Funds rapid asylum processing capacity. Costly; reduces border-crisis severity."
#,SkillsVisaFastTrack,Skills Visa Fast Track,"Fast-track visas for scarce skills. Growth upside; migration politics heat up."
#,SurgicalWaitCap,Surgical Wait Cap,"Legal maximum waits for key surgeries. Popular and expensive."
#,PandemicStockpileLaw,Pandemic Stockpile Law,"Mandatory medical stockpiles. Ongoing cost; dampens health crises."
```

Adjust column count/quoting to match the header exactly.

- [ ] **Step 4: Write IT translations (same keys)**

```csv
#,CarbonBorderAdjustment,Dazio carbonio alle frontiere,"Applica costi carbonio alle importazioni. Aiuta il clima ma alza prezzi e attriti commerciali."
#,GridStorageMandate,Obbligo di accumulo elettrico,"Impone stoccaggio elettrico su larga scala. Resilienza costosa contro i blackout."
#,RenovationWaveSubsidies,Sussidi ondata di ristrutturazioni,"Sussidi per ristrutturazioni profonde. Guadagni lenti su clima e qualità abitativa a alto costo."
#,RentStabilizationAct,Atto di stabilizzazione degli affitti,"Limita la crescita degli affitti. Popolare tra gli inquilini; scoraggia gli investimenti."
#,SocialHousingSurge,Spinta all'edilizia sociale,"Edilizia pubblica di massa. Costo di bilancio elevato; sollievo lento alla homelessnes."
#,AIWorkplaceAudit,Audit AI sui posti di lavoro,"Regola i licenziamenti automatizzati. Attutisce il backlash; rallenta la tech."
#,PublicComputeCloud,Cloud di calcolo pubblico,"Infrastruttura di calcolo pubblica. Capacità tech nel lungo periodo; forte pressione sul debito."
#,PlatformDutyOfCare,Dovere di cura delle piattaforme,"Responsabilità delle piattaforme per i danni. Più fiducia; attrito per business e tech."
#,AsylumProcessingSurge,Spinta ai processi di asilo,"Finanzia capacità di esame asilo. Costoso; riduce la gravità delle crisi di frontiera."
#,SkillsVisaFastTrack,Via preferenziale visti skill,"Visti rapidi per competenze rare. Crescita in più; tensione politica sull'immigrazione."
#,SurgicalWaitCap,Tetto attese chirurgiche,"Tempi massimi legali per interventi chiave. Popolare e costoso."
#,PandemicStockpileLaw,Legge scorte pandemiche,"Scorte mediche obbligatorie. Costo continuo; attenua le crisi sanitarie."
```

- [ ] **Step 5: Count check**

```powershell
$ids = @(
  "CarbonBorderAdjustment","GridStorageMandate","RenovationWaveSubsidies","RentStabilizationAct",
  "SocialHousingSurge","AIWorkplaceAudit","PublicComputeCloud","PlatformDutyOfCare",
  "AsylumProcessingSurge","SkillsVisaFastTrack","SurgicalWaitCap","PandemicStockpileLaw"
)
$pol = Get-Content "ModernPressureEU/data/simulation/policies.csv"
$en = Get-Content "ModernPressureEU/translations/english/policies.csv"
$it = Get-Content "ModernPressureEU/translations/italian/policies.csv"
foreach ($id in $ids) {
  if (-not ($pol | Where-Object { $_ -match "^#,$id," -or $_ -match "^#,$id\t" -or $_ -match "#,$id," })) { throw "policies missing $id" }
  if (-not ($en | Where-Object { $_ -match $id })) { throw "EN missing $id" }
  if (-not ($it | Where-Object { $_ -match $id })) { throw "IT missing $id" }
  if (-not ($pol | Where-Object { $_ -match $id -and $_ -match "_prereq_mod_eu" })) { throw "$id missing prereq" }
}
"OK 12 policies + translations"
```

Expected: `OK 12 policies + translations`.

- [ ] **Step 6: Commit**

```bash
git add ModernPressureEU/data/simulation/policies.csv ModernPressureEU/translations
git commit -m "feat: add 12 Modern Pressure EU policies with IT/EN strings"
```

---

### Task 5: Add 8 crisis events + locale strings

**Files:**
- Create: `ModernPressureEU/data/simulation/events/<files>.txt` (exact names from vanilla style; content `Name =` must match event IDs)
- Create/Modify: translation files for events as discovered in `reference/events_locale_note.md`

**Interfaces:**
- Consumes: `reference/sample_event.txt` structure (`[config]`, `OnImplement`, `[influences]`)
- Produces: 8 events gated by `_prereq_mod_eu`, with theme-pair mutual exclusion and A+/B− grudges

- [ ] **Step 1: Clone structure from sample event**

Read `reference/sample_event.txt`. Note keys: `Name`, `Texture`, `GUISound`, `OnImplement`, `[influences]` numbering.

- [ ] **Step 2: Write eight event files**

Create one file per event under `ModernPressureEU/data/simulation/events/`. Filenames: prefer `<Name>.txt` matching vanilla (e.g. `HeatGridFailure.txt`).

**Shared influence rules:**

1. Strong negative contribution unless `_prereq_mod_eu` is active. If influences cannot reference prereqs directly, use a high base only when a linked mission-only sim is present — **prefer**: first influence from `_prereq_mod_eu` if supported (same as policy PreReqs). If events cannot read prereqs, fall back to documenting that EU-only mission files are sufficient isolation for v1 **only after verifying** on a non-EU run (Acceptance #3). If verification fails, add a tiny EU-only situation or mission script grudge `ModEuActive` and key influences off that — keep YAGNI unless required.
2. `_random_,0,0.15` small noise.
3. Theme drivers (examples): low Environment / high Energy costs → heat/energy events; high Homelessness / low Housing → rent/mortgage; high Technology + Unemployment → AI layoff; low Health → hospital winter; high Immigration pressure → border collapse.
4. Mutual exclusion: each event’s `OnImplement` includes `CreateGrudge(<ThisEventName>,-0.95,0.92)` style self-suppression (copy vanilla self-grudge pattern from sample). Additionally, each event applies a moderate negative grudge to its theme sibling Name so the pair is less likely soon after.
5. Keep peak influence sums such that typical fire rate ≈ one serious event / 8–12 turns (events evaluate every 3 turns; threshold ~70% per docs). Prefer conservative bases; tune after playtest.

**OnImplement grudges (illustrative magnitudes — align to sample scale):**

| Name | Core grudges |
|------|----------------|
| HeatGridFailure | GDP−, Poor−, Environment reminder−; self-suppress |
| EnergyPriceSpike | GDP−, Capitalism−, Poor−; suppress EnergyPriceSpike + HeatGridFailure |
| RentStrikeWave | Socialist+, Capitalism−, Homelessness pressure; suppress pair |
| MortgageStress | MiddleIncome−, GDP−; suppress pair |
| AILayoffBacklash | Unemployment+, Technology−, Liberal anger; suppress pair |
| DeepfakeScandal | Political capital / trust targets per vanilla naming; suppress pair |
| BorderProcessingCollapse | Immigration crisis+, Conservative+/− tension per sample patterns |
| HospitalWinterCrisis | Health−, Parents−, Debt+; suppress |

Use only target names that exist in vanilla (verify against `simulation.csv` / sample events during implementation).

- [ ] **Step 3: Add EN + IT player-facing event text**

Follow the exact mechanism found in Task 1 (`events_locale_note.md`). Every event Name must have EN and IT title/description strings.

- [ ] **Step 4: File count check**

```powershell
$names = @(
  "HeatGridFailure","EnergyPriceSpike","RentStrikeWave","MortgageStress",
  "AILayoffBacklash","DeepfakeScandal","BorderProcessingCollapse","HospitalWinterCrisis"
)
$files = Get-ChildItem "ModernPressureEU/data/simulation/events" -Filter *.txt
if ($files.Count -ne 8) { throw "expected 8 event files, got $($files.Count)" }
foreach ($n in $names) {
  $hit = Select-String -Path $files.FullName -Pattern "Name\s*=\s*$n" -SimpleMatch:$false
  if (-not $hit) { throw "event Name missing $n" }
}
"OK 8 events"
```

Expected: `OK 8 events`.

- [ ] **Step 5: Commit**

```bash
git add ModernPressureEU/data/simulation/events ModernPressureEU/translations
git commit -m "feat: add 8 Modern Pressure EU crisis events with locales"
```

---

### Task 6: Validation script + install to Documents mods

**Files:**
- Create: `tools/validate-mod.ps1`
- Create: `tools/install-to-documents.ps1`

**Interfaces:**
- Consumes: finished `ModernPressureEU/` tree
- Produces: pass/fail structural gate + synced Documents install

- [ ] **Step 1: Write `tools/validate-mod.ps1`**

```powershell
$ErrorActionPreference = "Stop"
$root = "ModernPressureEU"
$ids = @(
  "CarbonBorderAdjustment","GridStorageMandate","RenovationWaveSubsidies","RentStabilizationAct",
  "SocialHousingSurge","AIWorkplaceAudit","PublicComputeCloud","PlatformDutyOfCare",
  "AsylumProcessingSurge","SkillsVisaFastTrack","SurgicalWaitCap","PandemicStockpileLaw"
)
$events = @(
  "HeatGridFailure","EnergyPriceSpike","RentStrikeWave","MortgageStress",
  "AILayoffBacklash","DeepfakeScandal","BorderProcessingCollapse","HospitalWinterCrisis"
)
if (-not (Test-Path "$root/config.txt")) { throw "missing config.txt" }
if ((Get-Content "$root/data/simulation/prereqs.txt" -Raw) -notmatch "_prereq_mod_eu") { throw "prereq not declared" }
$pol = Get-Content "$root/data/simulation/policies.csv"
$en = Get-Content "$root/translations/english/policies.csv"
$it = Get-Content "$root/translations/italian/policies.csv"
foreach ($id in $ids) {
  if (-not ($pol | Where-Object { $_ -match [regex]::Escape($id) -and $_ -match "^#" })) { throw "policy row $id" }
  if (-not ($pol | Where-Object { $_ -match [regex]::Escape($id) -and $_ -match "_prereq_mod_eu" })) { throw "prereq $id" }
  if (-not ($en | Where-Object { $_ -match [regex]::Escape($id) })) { throw "EN $id" }
  if (-not ($it | Where-Object { $_ -match [regex]::Escape($id) })) { throw "IT $id" }
}
$efiles = Get-ChildItem "$root/data/simulation/events" -Filter *.txt
if ($efiles.Count -ne 8) { throw "event file count $($efiles.Count)" }
foreach ($n in $events) {
  if (-not (Select-String -Path $efiles.FullName -Pattern "Name\s*=\s*$n")) { throw "event $n" }
}
$missions = Get-ChildItem "$root/data/missions" -Directory -ErrorAction Stop
if ($missions.Count -lt 1) { throw "no EU missions" }
foreach ($m in $missions) {
  $t = Get-ChildItem $m.FullName -Filter *.txt | Select-Object -First 1
  if ((Get-Content $t.FullName -Raw) -notmatch "(?im)_prereq_mod_eu\s*=\s*1") { throw "mission $($m.Name)" }
}
Write-Output "VALIDATE_OK"
```

- [ ] **Step 2: Write `tools/install-to-documents.ps1`**

```powershell
$ErrorActionPreference = "Stop"
$src = (Resolve-Path "ModernPressureEU").Path
$destParent = Join-Path $env:USERPROFILE "Documents\My Games\Democracy4\mods"
# fallback casing
if (-not (Test-Path (Split-Path $destParent -Parent))) {
  $alt = Join-Path $env:USERPROFILE "Documents\My Games\democracy4\mods"
  if (Test-Path (Split-Path $alt -Parent)) { $destParent = $alt }
}
New-Item -ItemType Directory -Force -Path $destParent | Out-Null
$dest = Join-Path $destParent "ModernPressureEU"
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Copy-Item $src $dest -Recurse
# ensure config path matches
$cfg = @"
[config]
name = ModernPressureEU
path = $dest
guiname = Modern Pressure EU
author = nicho
description = EU pressure pack: climate, housing, tech/AI, migration, health. Hard costs, slow payoffs, serious crises. Additive content + EU mission flag. Not a full economy overhaul.
"@
Set-Content -Path (Join-Path $dest "config.txt") -Value $cfg -Encoding utf8
Write-Output "INSTALLED=$dest"
```

- [ ] **Step 3: Run validate + install**

```powershell
powershell -NoProfile -File tools/validate-mod.ps1
powershell -NoProfile -File tools/install-to-documents.ps1
```

Expected: `VALIDATE_OK` then `INSTALLED=C:\Users\nicho\Documents\My Games\...`.

- [ ] **Step 4: Commit**

```bash
git add tools/validate-mod.ps1 tools/install-to-documents.ps1 ModernPressureEU/config.txt
git commit -m "chore: add ModernPressureEU validate and Documents install scripts"
```

---

### Task 7: In-game acceptance checklist (manual)

**Files:**
- Create: `docs/superpowers/plans/modern-pressure-eu-playtest.md` (checklist results)

**Interfaces:**
- Consumes: installed mod from Task 6
- Produces: filled checklist proving spec acceptance #1–#5

- [ ] **Step 1: Launch Democracy 4 → Mods**

Confirm **Modern Pressure EU** appears with correct guiname/description. Record pass/fail in playtest doc.

- [ ] **Step 2: EU mission smoke (France or Germany)**

New game, enable only this mod (plus required DLC if any). Confirm all 12 policies appear in the new-policy browser (search by GUI names). Switch language IT/EN if the game allows mid-session or via settings; confirm strings.

- [ ] **Step 3: Non-EU negative test (USA or UK)**

New game: confirm **none** of the 12 policy IDs/GUI names appear. Play until at least two event evaluation windows (~6+ turns) or use a temporary elevated-chance test build if needed; confirm mod events do not fire. Revert any temporary chance hikes before Workshop upload.

- [ ] **Step 4: Stability to turn 20 on EU**

No crash/softlock. Note any event fires (optional). If zero events by turn 40, raise influence bases slightly in a follow-up commit (keep mutual exclusion).

- [ ] **Step 5: Write results + commit**

```markdown
# Playtest results — Modern Pressure EU

Date:
Game build:

- [ ] Mods panel lists mod
- [ ] EU: 12 policies visible
- [ ] EU: IT + EN strings ok
- [ ] Non-EU: 0 mod policies
- [ ] Non-EU: 0 mod events
- [ ] EU turn 20: stable

Notes:
```

```bash
git add docs/superpowers/plans/modern-pressure-eu-playtest.md
git commit -m "test: record Modern Pressure EU in-game acceptance results"
```

- [ ] **Step 6: Workshop upload (manual, out of repo)**

In-game Workshop upload when playtest checklist is all checked. Do not automate Steam upload in this plan.

---

## Plan self-review

1. **Spec coverage:** Goal/approach F1 → Tasks 2–3; 12 policies → Task 4; 8 events + budget → Task 5; IT+EN → Tasks 4–5; Documents path → Task 6; acceptance → Task 7; non-goals respected (no vanilla economy rewrite).
2. **Placeholders:** None intentional; Task 1 gates on real install path; department tokens and effect target names must be copied from vanilla references at implement time (explicit step, not “TBD”).
3. **Consistency:** IDs/Names match spec; prereq `_prereq_mod_eu` used everywhere; EU mission list matches spec.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-10-03-modern-pressure-eu.md`. Two execution options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — execute tasks in this session with executing-plans checkpoints  

Which approach?
