# Modern Pressure EU v2 Deepen Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 20 policies + 12 crisis events to `ModernPressureEU` per `docs/superpowers/specs/2026-10-03-modern-pressure-eu-v2-design.md`, with burst pacing and priority-theme intensity.

**Architecture:** Same additive mod folder. Append policy CSV rows and new event `.txt` files gated on `_prereq_eu`. EN+IT translation rows + SVG icons. Extend `validate-mod.ps1` to assert totals 32 policies / 20 events. Deploy via `install-to-documents.ps1`.

**Tech Stack:** Democracy 4 data files (UTF-8 CSV + event INI `.txt`), PowerShell validation, existing v1 patterns in-repo.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-10-03-modern-pressure-eu-v2-design.md` (authoritative IDs).
- Do not rename/remove v1 IDs (12 policies / 8 events).
- Gate every new policy/event with `_prereq_eu` (not `_prereq_mod_eu`).
- No mission overrides; no new custom prereqs; no vanilla balance rewrites.
- Locales: `translations/English` + `translations/Italian` (capital E/I), identical keys.
- Priority intensity (climate/housing/migration): larger magnitudes than v1 retune; tech/health = v1 band.
- Burst: heavy-cluster sibling boost then long CreateGrudge; soft cross-cluster exclusion.
- Effect targets must exist in vanilla/mod (prefer v1-proven sims/groups). Avoid inventing sims (`Elderly`, `CoastalFlooding`, `WaterSupply` are invalid).
- CSV rows start with `#` in column A; UTF-8 no BOM preferred.
- Dev source: `ModernPressureEU/`; load: Documents `My Games\Democracy4\mods\ModernPressureEU`.
- ponytail: no extra frameworks, no separate expansion mod.

---

## File map

| Path | Responsibility |
|------|----------------|
| `ModernPressureEU/data/simulation/policies.csv` | Append 20 `#` policy rows |
| `ModernPressureEU/data/simulation/events/<Name>.txt` | 12 new event files |
| `ModernPressureEU/translations/English/policies.csv` | EN policy strings |
| `ModernPressureEU/translations/Italian/policies.csv` | IT policy strings |
| `ModernPressureEU/translations/English/events.csv` | EN event strings |
| `ModernPressureEU/translations/Italian/events.csv` | IT event strings |
| `ModernPressureEU/data/svg/icons_*.svg` | One icon per new policy |
| `ModernPressureEU/config.txt` | Description mentions v2 deepen |
| `tools/validate-mod.ps1` | Assert 32 policy IDs + 20 event Names |
| `tools/install-to-documents.ps1` | Keep description in sync with config |
| `docs/superpowers/plans/modern-pressure-eu-playtest.md` | Add v2 checklist lines |

---

### Task 1: Extend validator for v2 inventory (failing gate)

**Files:**
- Modify: `tools/validate-mod.ps1`

**Interfaces:**
- Consumes: current mod tree (still v1-only content)
- Produces: validator that expects full v1+v2 lists and fails until later tasks land

- [ ] **Step 1: Replace ID arrays and event count in `tools/validate-mod.ps1`**

```powershell
$ErrorActionPreference = "Stop"
$root = "ModernPressureEU"
$ids = @(
  # v1
  "CarbonBorderAdjustment","GridStorageMandate","RenovationWaveSubsidies","RentStabilizationAct",
  "SocialHousingSurge","AIWorkplaceAudit","PublicComputeCloud","PlatformDutyOfCare",
  "AsylumProcessingSurge","SkillsVisaFastTrack","SurgicalWaitCap","PandemicStockpileLaw",
  # v2 climate
  "HeatPumpMandate","AgriMethaneCap","IndustrialElectrificationFund","DroughtWaterRationing",
  "CoastalDefenseLevy","NuclearLifeExtension",
  # v2 housing
  "VacancyTax","ShortTermRentalCap","FirstHomeGuarantee","LandlordEnergyUpgradeDuty",
  "AntiEvictionMoratorium","UrbanDensificationAct",
  # v2 migration / tech / health
  "ExternalAsylumHubs","LocalReceptionQuota","LabourInspectionBlitz","CitizenshipTrackReform",
  "SchengenFlexControls","AlgorithmicPublicServices","MentalHealthAccessAct","ElderCareInsurance"
)
$events = @(
  # v1
  "HeatGridFailure","EnergyPriceSpike","RentStrikeWave","MortgageStress",
  "AILayoffBacklash","DeepfakeScandal","BorderProcessingCollapse","HospitalWinterCrisis",
  # v2
  "CropFailureDrought","CoastalFloodShock","HomelessCampCrisis","LandlordExodus",
  "ReceptionCenterRiot","SmugglerCorridorSpike","PublicDataLeak","AutomationStrike",
  "AmbulanceGridlock","CareHomeOutbreak","CostOfLivingMarch","EUFiscalWarning"
)
if (-not (Test-Path "$root/config.txt")) { throw "missing config.txt" }
$pol = Get-Content "$root/data/simulation/policies.csv"
$en = Get-Content "$root/translations/English/policies.csv"
$it = Get-Content "$root/translations/Italian/policies.csv"
foreach ($id in $ids) {
  if (-not ($pol | Where-Object { $_ -match [regex]::Escape($id) -and $_ -match "^#" })) { throw "policy row $id" }
  if (-not ($pol | Where-Object { $_ -match [regex]::Escape($id) -and $_ -match "_prereq_eu" })) { throw "prereq $id" }
  if (-not ($en | Where-Object { $_ -match [regex]::Escape($id) })) { throw "EN $id" }
  if (-not ($it | Where-Object { $_ -match [regex]::Escape($id) })) { throw "IT $id" }
  $icon = Join-Path $root ("data/svg/icons_{0}.svg" -f $id.ToLower())
  if (-not (Test-Path $icon)) { throw "missing icon $icon" }
}
$efiles = Get-ChildItem "$root/data/simulation/events" -Filter *.txt
if ($efiles.Count -ne 20) { throw "event file count $($efiles.Count)" }
foreach ($n in $events) {
  if (-not (Select-String -Path $efiles.FullName -Pattern "Name\s*=\s*$n")) { throw "event $n" }
}
foreach ($f in $efiles) {
  if ((Get-Content $f.FullName -Raw) -notmatch '_prereq_eu') { throw "event $($f.Name) missing _prereq_eu" }
}
$enEv = Get-Content "$root/translations/English/events.csv"
$itEv = Get-Content "$root/translations/Italian/events.csv"
foreach ($n in $events) {
  if (-not ($enEv | Where-Object { $_ -match [regex]::Escape($n) })) { throw "EN event $n" }
  if (-not ($itEv | Where-Object { $_ -match [regex]::Escape($n) })) { throw "IT event $n" }
}
Write-Output "VALIDATE_OK"
```

- [ ] **Step 2: Run validator — expect FAIL**

```powershell
powershell -NoProfile -File tools/validate-mod.ps1
```

Expected: throws on first missing v2 policy (e.g. `policy row HeatPumpMandate`).

- [ ] **Step 3: Commit**

```powershell
git add tools/validate-mod.ps1
git commit -m "test: extend validate-mod for v2 inventory"
```

---

### Task 2: Climate + housing policies (12) + locales + icons

**Files:**
- Modify: `ModernPressureEU/data/simulation/policies.csv`
- Modify: `ModernPressureEU/translations/English/policies.csv`
- Modify: `ModernPressureEU/translations/Italian/policies.csv`
- Create: `ModernPressureEU/data/svg/icons_<id>.svg` for each of the 12 IDs

**Interfaces:**
- Consumes: v1 CSV column shape; vanilla SVG sources via `reference/game_path.txt`
- Produces: 12 gated `#` policy rows (priority intensity) + EN/IT + icons

- [ ] **Step 1: Append these 12 rows to `policies.csv` (after last v1 row)**

```csv
#,HeatPumpMandate,default,,,14,20,9,9,ECONOMY,_prereq_eu,1800,9000,0+(1.0*x),,5,0,0,0+(1.0*x),,,#Effects,"EnergyEfficiency,0.08+(0.30*x),4","CO2Emissions,-0.06-(0.22*x),4","GDP,-0.05-(0.14*x),3","Capitalist,-0.08-(0.22*x),3","Poor,-0.03-(0.10*x),3","Farmers,-0.04-(0.12*x),3",,,,,,,,,,,
#,AgriMethaneCap,default,,,12,18,8,9,ECONOMY,_prereq_eu,400,2800,0+(1.0*x),,3,0,0,0+(1.0*x),,,#Effects,"Environment,0.05+(0.18*x),4","CO2Emissions,-0.05-(0.18*x),4","Farmers,-0.14-(0.32*x),3","FoodPrice,0.04+(0.14*x),3","GDP,-0.03-(0.10*x),3","Capitalist,-0.05-(0.14*x),3",,,,,,,,,,,
#,IndustrialElectrificationFund,default,,,15,22,10,11,ECONOMY,_prereq_eu,2800,14000,0+(1.0*x),,5,0,0,0+(1.0*x),,,#Effects,"CO2Emissions,-0.07-(0.24*x),5","EnergyEfficiency,0.05+(0.20*x),5","Debt,0.05+(0.16*x),4","GDP,-0.04-(0.12*x),3","Capitalist,-0.06-(0.16*x),3","Unemployment,-0.02-(0.08*x),4",,,,,,,,,,,
#,DroughtWaterRationing,default,,,10,16,7,8,LAWANDORDER,_prereq_eu,150,1200,0+(1.0*x),,3,0,0,0+(1.0*x),,,#Effects,"Environment,0.04+(0.14*x),3","Agriculture,-0.08-(0.24*x),3","Farmers,-0.12-(0.28*x),3","Tourism,-0.06-(0.18*x),3","_All_,-0.04-(0.12*x),3","Poor,-0.05-(0.14*x),3",,,,,,,,,,,
#,CoastalDefenseLevy,default,,,13,19,9,10,ECONOMY,_prereq_eu,900,5500,0+(1.0*x),,4,0,0,0+(1.0*x),,,#Effects,"Environment,0.03+(0.12*x),4","Debt,-0.02-(0.06*x),3","GDP,-0.04-(0.12*x),3","Capitalist,-0.06-(0.16*x),3","_All_,-0.03-(0.10*x),3","Tourism,0.02+(0.08*x),4",,,,,,,,,,,
#,NuclearLifeExtension,default,,,16,24,10,12,ECONOMY,_prereq_eu,2200,12000,0+(1.0*x),,5,0,0,0+(1.0*x),,,#Effects,"EnergyEfficiency,0.06+(0.24*x),5","CO2Emissions,-0.05-(0.18*x),4","Environment,-0.04-(0.14*x),3","GDP,0.02+(0.08*x),4","Liberal,-0.08-(0.20*x),3","Capitalist,0.03+(0.10*x),3",,,,,,,,,,,
#,VacancyTax,default,,,11,17,8,9,WELFARE,_prereq_eu,200,1800,0+(1.0*x),,3,0,0,0+(1.0*x),,,#Effects,"Homelessness,-0.06-(0.20*x),4","Poor,0.05+(0.16*x),3","PrivateHousing,-0.08-(0.22*x),3","Capitalist,-0.14-(0.30*x),3","GDP,-0.03-(0.10*x),3","MiddleIncome,0.02+(0.08*x),3",,,,,,,,,,,
#,ShortTermRentalCap,default,,,12,18,8,9,WELFARE,_prereq_eu,250,2000,0+(1.0*x),,3,0,0,0+(1.0*x),,,#Effects,"Homelessness,-0.05-(0.18*x),4","Tourism,-0.10-(0.26*x),3","PrivateHousing,-0.06-(0.18*x),3","Capitalist,-0.12-(0.26*x),3","Poor,0.04+(0.14*x),3","GDP,-0.03-(0.10*x),3",,,,,,,,,,,
#,FirstHomeGuarantee,default,,,14,21,9,11,WELFARE,_prereq_eu,1600,9000,0+(1.0*x),,4,0,0,0+(1.0*x),,,#Effects,"MiddleIncome,0.08+(0.24*x),4","Homelessness,-0.04-(0.14*x),4","Debt,0.06+(0.20*x),4","GDP,-0.03-(0.08*x),3","Capitalist,-0.05-(0.14*x),3","_All_,0.02+(0.06*x),3",,,,,,,,,,,
#,LandlordEnergyUpgradeDuty,default,,,13,19,9,10,WELFARE,_prereq_eu,300,2200,0+(1.0*x),,4,0,0,0+(1.0*x),,,#Effects,"EnergyEfficiency,0.05+(0.20*x),4","CO2Emissions,-0.04-(0.14*x),4","PrivateHousing,-0.10-(0.24*x),3","Capitalist,-0.14-(0.30*x),3","Poor,0.04+(0.12*x),3","GDP,-0.03-(0.10*x),3",,,,,,,,,,,
#,AntiEvictionMoratorium,default,,,10,16,7,8,WELFARE,_prereq_eu,180,1400,0+(1.0*x),,3,0,0,0+(1.0*x),,,#Effects,"Poor,0.10+(0.28*x),3","Socialist,0.08+(0.22*x),3","Homelessness,-0.06-(0.18*x),3","Capitalist,-0.16-(0.34*x),3","PrivateHousing,-0.10-(0.24*x),3","GDP,-0.04-(0.12*x),3",,,,,,,,,,,
#,UrbanDensificationAct,default,,,14,20,9,10,WELFARE,_prereq_eu,700,4500,0+(1.0*x),,4,0,0,0+(1.0*x),,,#Effects,"Homelessness,-0.07-(0.22*x),5","PrivateHousing,0.04+(0.14*x),5","GDP,0.02+(0.08*x),4","MiddleIncome,-0.06-(0.18*x),3","Conservatives,-0.08-(0.20*x),3","Environment,-0.03-(0.10*x),3",,,,,,,,,,,
```

- [ ] **Step 2: Append EN strings to `translations/English/policies.csv`**

```csv
#,HeatPumpMandate,Heat Pump Mandate,"Forces heat-pump adoption. Cuts emissions, hits households and business hard."
#,AgriMethaneCap,Agri Methane Cap,"Caps farm methane. Helps climate, enrages farmers and raises food prices."
#,IndustrialElectrificationFund,Industrial Electrification Fund,"Huge fund to electrify industry. Slow green gains, fast debt pressure."
#,DroughtWaterRationing,Drought Water Rationing,"Emergency water limits. Unpopular with farmers, tourism and the poor."
#,CoastalDefenseLevy,Coastal Defense Levy,"Taxes coastal defence works. Fiscal drag now for climate risk later."
#,NuclearLifeExtension,Nuclear Life Extension,"Keeps reactors online longer. Energy up, greens and liberals hostile."
#,VacancyTax,Vacancy Tax,"Taxes empty homes. Helps housing pressure, landlords furious."
#,ShortTermRentalCap,Short-Term Rental Cap,"Caps short-lets. Freeing homes costs tourism and landlords."
#,FirstHomeGuarantee,First-Home Guarantee,"State-backed first homes. Middle class love it; debt climbs."
#,LandlordEnergyUpgradeDuty,Landlord Energy Upgrade Duty,"Forces landlord efficiency upgrades. Climate up, landlords revolt."
#,AntiEvictionMoratorium,Anti-Eviction Moratorium,"Blocks evictions. Popular with the poor; housing market freezes."
#,UrbanDensificationAct,Urban Densification Act,"Forces denser building. More homes, suburban NIMBY backlash."
```

- [ ] **Step 3: Append IT strings to `translations/Italian/policies.csv`**

```csv
#,HeatPumpMandate,"Obbligo pompe di calore","Impone le pompe di calore. Taglia emissioni, colpisce famiglie e imprese."
#,AgriMethaneCap,"Tetto al metano agricolo","Limita il metano agricolo. Aiuta il clima, fa esplodere agricoltori e prezzi cibo."
#,IndustrialElectrificationFund,"Fondo elettrificazione industriale","Fondo enorme per elettrificare l'industria. Verde lento, debito veloce."
#,DroughtWaterRationing,"Razionamento idrico per siccita'","Limiti idrici d'emergenza. Agricoltori, turismo e poveri contro."
#,CoastalDefenseLevy,"Tassa difesa costiera","Finanzia opere costiere. Costa ora, riduce rischi climatici dopo."
#,NuclearLifeExtension,"Estensione vita nucleare","Prolunga i reattori. Energia su, verdi e liberali ostili."
#,VacancyTax,"Tassa sulle case vuote","Tassa gli immobili vuoti. Aiuta la casa, padroni di casa furiosi."
#,ShortTermRentalCap,"Tetto agli affitti brevi","Limita gli affitti brevi. Piu' case, meno turismo e rendite."
#,FirstHomeGuarantee,"Garanzia prima casa","Garanzia pubblica per la prima casa. Classe media contenta, debito su."
#,LandlordEnergyUpgradeDuty,"Obbligo efficientamento ai proprietari","Obbliga i proprietari a efficientare. Clima su, padroni in rivolta."
#,AntiEvictionMoratorium,"Moratoria sugli sfratti","Blocca gli sfratti. Poveri contenti, mercato immobiliare ghiacciato."
#,UrbanDensificationAct,"Legge sulla densificazione urbana","Impone edifici piu' densi. Piu' case, NIMBY suburbani contro."
```

- [ ] **Step 4: Copy icons from vanilla**

```powershell
$g = (Get-Content reference/game_path.txt -Raw).Trim()
$src = Join-Path $g "data\svg"
$dst = "ModernPressureEU\data\svg"
$map = @{
  "icons_heatpumpmandate.svg" = "icons_electriccartransition.svg"
  "icons_agrimethanecap.svg" = "icons_agriculture.svg"
  "icons_industrialelectrificationfund.svg" = "icons_industry.svg"
  "icons_droughtwaterrationing.svg" = "icons_water.svg"
  "icons_coastaldefenselevy.svg" = "icons_climatechangeadaptionfund.svg"
  "icons_nuclearlifeextension.svg" = "icons_nuclear.svg"
  "icons_vacancytax.svg" = "icons_propertytax.svg"
  "icons_shorttermrentalcap.svg" = "icons_rentcontrols.svg"
  "icons_firsthomeguarantee.svg" = "icons_statehousing.svg"
  "icons_landlordenergyupgradeduty.svg" = "icons_energyefficiency.svg"
  "icons_antievictionmoratorium.svg" = "icons_legalaid.svg"
  "icons_urbandensificationact.svg" = "icons_construction.svg"
}
foreach ($kv in $map.GetEnumerator()) {
  $from = Join-Path $src $kv.Value
  if (-not (Test-Path $from)) {
    $alt = Get-ChildItem $src -Filter "*.svg" | Where-Object { $_.Name -match ($kv.Value -replace 'icons_|\.svg','') } | Select-Object -First 1
    if (-not $alt) { throw "missing icon source $($kv.Value)" }
    $from = $alt.FullName
  }
  Copy-Item $from (Join-Path $dst $kv.Key) -Force
  "OK $($kv.Key)"
}
```

If a source name is missing, pick the closest existing vanilla `icons_*.svg` and keep the destination filename exact.

- [ ] **Step 5: Spot-check row counts**

```powershell
python -c "import csv; from pathlib import Path
p=list(csv.reader(Path('ModernPressureEU/data/simulation/policies.csv').open(encoding='utf-8')))
print('policy_rows', sum(1 for r in p if r and r[0]=='#'))
"
```

Expected: `policy_rows 24` (12 v1 + 12 this task).

- [ ] **Step 6: Commit**

```powershell
git add ModernPressureEU/data/simulation/policies.csv ModernPressureEU/translations/English/policies.csv ModernPressureEU/translations/Italian/policies.csv ModernPressureEU/data/svg
git commit -m "feat: add v2 climate and housing policies"
```

---

### Task 3: Migration + tech + health policies (8) + locales + icons

**Files:**
- Modify: same policy/translation CSV paths as Task 2
- Create: 8 more SVG icons

**Interfaces:**
- Consumes: Task 2 CSV append style
- Produces: full 32 policy rows

- [ ] **Step 1: Append 8 policy rows**

```csv
#,ExternalAsylumHubs,default,,,14,22,9,11,FOREIGNPOLICY,_prereq_eu,1400,8000,0+(1.0*x),,4,0,0,0+(1.0*x),,,#Effects,"IllegalImmigration,-0.08-(0.24*x),4","Immigration,-0.05-(0.16*x),4","Conservatives,0.08+(0.22*x),3","Patriot,0.06+(0.18*x),3","Liberal,-0.12-(0.28*x),3","ForeignRelations,-0.08-(0.22*x),3","GDP,-0.03-(0.10*x),3",,,,,,,,,,
#,LocalReceptionQuota,default,,,12,18,8,9,FOREIGNPOLICY,_prereq_eu,600,4000,0+(1.0*x),,3,0,0,0+(1.0*x),,,#Effects,"Immigration,0.03+(0.10*x),3","RacialTension,0.06+(0.20*x),3","Conservatives,-0.08-(0.22*x),3","Liberal,0.05+(0.14*x),3","Poor,-0.04-(0.12*x),3","_All_,-0.03-(0.08*x),3",,,,,,,,,,,
#,LabourInspectionBlitz,default,,,11,17,7,8,LAWANDORDER,_prereq_eu,350,2400,0+(1.0*x),,3,0,0,0+(1.0*x),,,#Effects,"IllegalImmigration,-0.07-(0.22*x),4","Crime,-0.03-(0.10*x),3","Capitalist,-0.10-(0.24*x),3","Unemployment,0.02+(0.08*x),3","GDP,-0.03-(0.10*x),3","Conservatives,0.04+(0.12*x),3",,,,,,,,,,,
#,CitizenshipTrackReform,default,,,13,19,8,10,FOREIGNPOLICY,_prereq_eu,400,2800,0+(1.0*x),,4,0,0,0+(1.0*x),,,#Effects,"Immigration,0.04+(0.14*x),3","Equality,0.04+(0.14*x),4","Liberal,0.06+(0.18*x),3","Conservatives,-0.10-(0.24*x),3","Patriot,-0.08-(0.20*x),3","RacialTension,-0.03-(0.10*x),4",,,,,,,,,,,
#,SchengenFlexControls,default,,,12,18,8,9,FOREIGNPOLICY,_prereq_eu,500,3200,0+(1.0*x),,3,0,0,0+(1.0*x),,,#Effects,"IllegalImmigration,-0.06-(0.18*x),3","Crime,-0.03-(0.10*x),3","ForeignRelations,-0.10-(0.24*x),3","Conservatives,0.06+(0.16*x),3","Liberal,-0.08-(0.20*x),3","InternationalTrade,-0.04-(0.12*x),3",,,,,,,,,,,
#,AlgorithmicPublicServices,default,,,12,18,8,9,PUBLICSERVICES,_prereq_eu,800,4500,0+(1.0*x),,4,0,0,0+(1.0*x),,,#Effects,"Technology,0.04+(0.16*x),4","Debt,-0.02-(0.06*x),4","_percept_trust,-0.05-(0.16*x),3","Liberal,-0.04-(0.12*x),3","Unemployment,0.02+(0.08*x),3","GDP,0.01+(0.05*x),4",,,,,,,,,,,
#,MentalHealthAccessAct,default,,,14,21,9,11,PUBLICSERVICES,_prereq_eu,1800,10000,0+(1.0*x),,4,0,0,0+(1.0*x),,,#Effects,"Health,0.06+(0.22*x),4","Poor,0.05+(0.14*x),3","Parents,0.04+(0.12*x),3","GDP,-0.05-(0.14*x),3","Debt,0.04+(0.12*x),3","_All_,0.03+(0.08*x),3",,,,,,,,,,,
#,ElderCareInsurance,default,,,15,22,10,12,PUBLICSERVICES,_prereq_eu,2200,12000,0+(1.0*x),,5,0,0,0+(1.0*x),,,#Effects,"Health,0.05+(0.18*x),5","Parents,0.08+(0.22*x),4","Debt,0.06+(0.18*x),4","GDP,-0.04-(0.12*x),3","Capitalist,-0.05-(0.14*x),3","_All_,0.02+(0.06*x),3",,,,,,,,,,,
```

Note: if `Equality` is not a valid effect target in your install (sim/situation), replace that cell with `Liberal,0.04+(0.14*x),4`.

- [ ] **Step 2: Append EN + IT translation rows**

EN:

```csv
#,ExternalAsylumHubs,External Asylum Hubs,"Processes asylum offshore. Right-leaning relief; liberals and diplomacy pay."
#,LocalReceptionQuota,Local Reception Quota,"Forces local reception quotas. Spreads the load, raises local tension."
#,LabourInspectionBlitz,Labour Inspection Blitz,"Raids illegal labour. Cuts shadow work, angers business."
#,CitizenshipTrackReform,Citizenship Track Reform,"Reforms citizenship tracks. Integration path with culture-war heat."
#,SchengenFlexControls,Schengen Flex Controls,"Flexible internal border controls. Security up, EU relations down."
#,AlgorithmicPublicServices,Algorithmic Public Services,"Automates public services. Some efficiency, trust and privacy costs."
#,MentalHealthAccessAct,Mental Health Access Act,"Expands mental-health access. Popular and expensive."
#,ElderCareInsurance,Elder Care Insurance,"Mandatory elder-care cover. Families relieved; debt climbs."
```

IT:

```csv
#,ExternalAsylumHubs,"Hub esterni per l'asilo","Gestisce l'asilo all'estero. Destra sollevata; liberali e diplomazia pagano."
#,LocalReceptionQuota,"Quote di accoglienza locali","Impone quote locali. Distribuisce il carico, alza la tensione."
#,LabourInspectionBlitz,"Blitz ispezioni sul lavoro","Colpisce il lavoro nero. Meno sommerso, impresa arrabbiata."
#,CitizenshipTrackReform,"Riforma percorsi di cittadinanza","Riforma i percorsi di cittadinanza. Integrazione con guerra culturale."
#,SchengenFlexControls,"Controlli flessibili Schengen","Controlli interni flessibili. Sicurezza su, rapporti UE giu'."
#,AlgorithmicPublicServices,"Servizi pubblici algoritmici","Automatizza la PA. Un po' di efficienza, costi di fiducia e privacy."
#,MentalHealthAccessAct,"Accesso alla salute mentale","Espande la salute mentale. Popolare e costoso."
#,ElderCareInsurance,"Assicurazione cura anziani","Copertura obbligatoria per gli anziani. Famiglie sollevate, debito su."
```

- [ ] **Step 3: Copy icons**

```powershell
$g = (Get-Content reference/game_path.txt -Raw).Trim()
$src = Join-Path $g "data\svg"
$dst = "ModernPressureEU\data\svg"
$map = @{
  "icons_externalasylumhubs.svg" = "icons_immigration.svg"
  "icons_localreceptionquota.svg" = "icons_immigrationrules.svg"
  "icons_labourinspectionblitz.svg" = "icons_labourlaws.svg"
  "icons_citizenshiptrackreform.svg" = "icons_equality.svg"
  "icons_schengenflexcontrols.svg" = "icons_border.svg"
  "icons_algorithmicpublicservices.svg" = "icons_technology.svg"
  "icons_mentalhealthaccessact.svg" = "icons_health.svg"
  "icons_eldercareinsurance.svg" = "icons_healthcarevouchers.svg"
}
foreach ($kv in $map.GetEnumerator()) {
  $from = Join-Path $src $kv.Value
  if (-not (Test-Path $from)) {
    $alt = Get-ChildItem $src -Filter "icons_*.svg" | Select-Object -First 1
    if (-not $alt) { throw "no svg sources" }
    $from = $alt.FullName
    Write-Warning "fallback $($kv.Key) <- $($alt.Name)"
  }
  Copy-Item $from (Join-Path $dst $kv.Key) -Force
}
```

- [ ] **Step 4: Confirm 32 policy rows**

```powershell
python -c "import csv; from pathlib import Path
p=list(csv.reader(Path('ModernPressureEU/data/simulation/policies.csv').open(encoding='utf-8')))
print('policy_rows', sum(1 for r in p if r and r[0]=='#'))"
```

Expected: `policy_rows 32`.

- [ ] **Step 5: Commit**

```powershell
git add ModernPressureEU/data/simulation/policies.csv ModernPressureEU/translations ModernPressureEU/data/svg
git commit -m "feat: add v2 migration tech health policies"
```

---

### Task 4: Heavy-cluster burst events (6) + locales

**Files:**
- Create: `ModernPressureEU/data/simulation/events/CropFailureDrought.txt`
- Create: `ModernPressureEU/data/simulation/events/CoastalFloodShock.txt`
- Create: `ModernPressureEU/data/simulation/events/HomelessCampCrisis.txt`
- Create: `ModernPressureEU/data/simulation/events/LandlordExodus.txt`
- Create: `ModernPressureEU/data/simulation/events/ReceptionCenterRiot.txt`
- Create: `ModernPressureEU/data/simulation/events/SmugglerCorridorSpike.txt`
- Modify: `ModernPressureEU/translations/English/events.csv`
- Modify: `ModernPressureEU/translations/Italian/events.csv`

**Interfaces:**
- Consumes: v1 event shape (`HeatGridFailure.txt`)
- Produces: 3 burst pairs with sibling boost + long self/sibling grudges

- [ ] **Step 1: Write climate pair**

`CropFailureDrought.txt`:

```txt
[config]
Name = CropFailureDrought
Texture = event25.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(CropFailureDrought,-0.92,0.88);CreateGrudge(CoastalFloodShock,-0.15,0.55);CreateGrudge(FoodPrice,0.20,0.82);CreateGrudge(Farmers,-0.22,0.80);CreateGrudge(Poor,-0.16,0.80);CreateGrudge(GDP,-0.12,0.82);CreateGrudge(HeatGridFailure,-0.35,0.75);CreateGrudge(EnergyPriceSpike,-0.30,0.75);

[influences]
0 = _random_,0.04,0.24
1 = AverageTemperature,0+(0.40*x)
2 = Agriculture,0.28-(0.28*x)
3 = Environment,0.22-(0.22*x)
4 = _prereq_,_prereq_eu
```

`CoastalFloodShock.txt`:

```txt
[config]
Name = CoastalFloodShock
Texture = event25.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(CoastalFloodShock,-0.92,0.88);CreateGrudge(CropFailureDrought,-0.15,0.55);CreateGrudge(Environment,-0.16,0.82);CreateGrudge(Tourism,-0.18,0.80);CreateGrudge(GDP,-0.14,0.80);CreateGrudge(_All_,-0.10,0.82);CreateGrudge(HeatGridFailure,-0.30,0.75);CreateGrudge(EnergyPriceSpike,-0.28,0.75);

[influences]
0 = _random_,0.04,0.24
1 = AverageTemperature,0+(0.36*x)
2 = Environment,0.26-(0.26*x)
3 = Debt,0+(0.18*x)
4 = _prereq_,_prereq_eu
```

Burst note: first event’s `CreateGrudge(Sibling,-0.15,0.55)` is a **mild** suppress so the sibling can still fire soon; after both fire, each applies strong self-grudge. Also soft-suppress v1 climate pair.

- [ ] **Step 2: Write housing pair**

`HomelessCampCrisis.txt`:

```txt
[config]
Name = HomelessCampCrisis
Texture = event_flashcrash.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(HomelessCampCrisis,-0.92,0.88);CreateGrudge(LandlordExodus,-0.15,0.55);CreateGrudge(Homelessness,0.18,0.82);CreateGrudge(Poor,-0.20,0.80);CreateGrudge(Crime,0.10,0.82);CreateGrudge(_All_,-0.08,0.82);CreateGrudge(RentStrikeWave,-0.35,0.75);CreateGrudge(MortgageStress,-0.30,0.75);

[influences]
0 = _random_,0.04,0.24
1 = Homelessness,0+(0.42*x)
2 = PovertyRate,0+(0.28*x)
3 = PrivateHousing,0.20-(0.20*x)
4 = _prereq_,_prereq_eu
```

`LandlordExodus.txt`:

```txt
[config]
Name = LandlordExodus
Texture = event_flashcrash.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(LandlordExodus,-0.92,0.88);CreateGrudge(HomelessCampCrisis,-0.15,0.55);CreateGrudge(PrivateHousing,-0.20,0.82);CreateGrudge(Homelessness,0.14,0.80);CreateGrudge(Capitalist,-0.16,0.80);CreateGrudge(GDP,-0.10,0.82);CreateGrudge(RentStrikeWave,-0.30,0.75);CreateGrudge(MortgageStress,-0.32,0.75);

[influences]
0 = _random_,0.04,0.24
1 = PrivateHousing,0.30-(0.30*x)
2 = GDP,0.18-(0.18*x)
3 = Homelessness,0+(0.22*x)
4 = _prereq_,_prereq_eu
```

- [ ] **Step 3: Write migration pair**

`ReceptionCenterRiot.txt`:

```txt
[config]
Name = ReceptionCenterRiot
Texture = event25.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(ReceptionCenterRiot,-0.92,0.88);CreateGrudge(SmugglerCorridorSpike,-0.15,0.55);CreateGrudge(RacialTension,0.18,0.82);CreateGrudge(Crime,0.12,0.80);CreateGrudge(Conservatives,-0.10,0.80);CreateGrudge(Liberal,-0.08,0.82);CreateGrudge(BorderProcessingCollapse,-0.35,0.75);

[influences]
0 = _random_,0.04,0.24
1 = Immigration,0+(0.36*x)
2 = RacialTension,0+(0.32*x)
3 = Crime,0+(0.18*x)
4 = _prereq_,_prereq_eu
```

`SmugglerCorridorSpike.txt`:

```txt
[config]
Name = SmugglerCorridorSpike
Texture = event25.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(SmugglerCorridorSpike,-0.92,0.88);CreateGrudge(ReceptionCenterRiot,-0.15,0.55);CreateGrudge(IllegalImmigration,0.20,0.82);CreateGrudge(Crime,0.14,0.80);CreateGrudge(Patriot,-0.12,0.80);CreateGrudge(ForeignRelations,-0.10,0.82);CreateGrudge(BorderProcessingCollapse,-0.32,0.75);

[influences]
0 = _random_,0.04,0.24
1 = IllegalImmigration,0+(0.40*x)
2 = Immigration,0+(0.22*x)
3 = Crime,0+(0.16*x)
4 = _prereq_,_prereq_eu
```

- [ ] **Step 4: Append EN/IT event strings**

EN:

```csv
#,CropFailureDrought,Crop Failure Drought,"Drought has destroyed harvests, pushing food prices up and rural anger higher."
#,CoastalFloodShock,Coastal Flood Shock,"A coastal flood has damaged homes, tourism and public finances."
#,HomelessCampCrisis,Homeless Camp Crisis,"Growing homeless camps have become a public-order and welfare flashpoint."
#,LandlordExodus,Landlord Exodus,"Landlords are exiting the rental market, shrinking housing supply fast."
#,ReceptionCenterRiot,Reception Center Riot,"Violence at a reception centre has ignited a national immigration row."
#,SmugglerCorridorSpike,Smuggler Corridor Spike,"Smuggling routes have surged, overwhelming border controls."
```

IT:

```csv
#,CropFailureDrought,"Raccolti distrutti dalla siccita'","La siccita' ha rovinato i raccolti: prezzi del cibo su e rabbia rurale."
#,CoastalFloodShock,"Shock alluvione costiera","Un'alluvione costiera ha colpito case, turismo e bilanci pubblici."
#,HomelessCampCrisis,"Crisi degli accampamenti","Gli accampamenti di senzatetto sono diventati un'emergenza di ordine e welfare."
#,LandlordExodus,"Fuga dei proprietari","I padroni di casa escono dal mercato degli affitti: offerta in crollo."
#,ReceptionCenterRiot,"Rivolta al centro di accoglienza","Violenze in un centro di accoglienza: caso nazionale sull'immigrazione."
#,SmugglerCorridorSpike,"Picco dei corridoi del traffico","Le rotte dei trafficanti sono esplose e i controlli di frontiera cedono."
```

- [ ] **Step 5: Commit**

```powershell
git add ModernPressureEU/data/simulation/events ModernPressureEU/translations/English/events.csv ModernPressureEU/translations/Italian/events.csv
git commit -m "feat: add v2 heavy-cluster burst events"
```

---

### Task 5: Light + cross events (6) + locales + cross-cluster soft exclusion

**Files:**
- Create: `PublicDataLeak.txt`, `AutomationStrike.txt`, `AmbulanceGridlock.txt`, `CareHomeOutbreak.txt`, `CostOfLivingMarch.txt`, `EUFiscalWarning.txt` under `ModernPressureEU/data/simulation/events/`
- Modify: EN/IT `events.csv`
- Modify: the 6 heavy-cluster event files from Task 4 (add soft grudges vs other heavy clusters)

**Interfaces:**
- Consumes: Task 4 burst pairs
- Produces: 20 total events; soft exclusion between heavy clusters

- [ ] **Step 1: Write light/cross event files**

`PublicDataLeak.txt`:

```txt
[config]
Name = PublicDataLeak
Texture = event_flashcrash.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(PublicDataLeak,-0.90,0.90);CreateGrudge(AutomationStrike,-0.55,0.85);CreateGrudge(_percept_trust,-0.18,0.82);CreateGrudge(Liberal,-0.10,0.80);CreateGrudge(Technology,-0.08,0.84);

[influences]
0 = _random_,0.03,0.18
1 = Technology,0+(0.28*x)
2 = _percept_trust,0.24-(0.24*x)
3 = _prereq_,_prereq_eu
```

`AutomationStrike.txt`:

```txt
[config]
Name = AutomationStrike
Texture = event_flashcrash.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(AutomationStrike,-0.90,0.90);CreateGrudge(PublicDataLeak,-0.55,0.85);CreateGrudge(Unemployment,0.14,0.82);CreateGrudge(GDP,-0.10,0.82);CreateGrudge(Technology,-0.08,0.84);CreateGrudge(AILayoffBacklash,-0.40,0.80);

[influences]
0 = _random_,0.03,0.18
1 = Unemployment,0+(0.30*x)
2 = Technology,0+(0.22*x)
3 = _prereq_,_prereq_eu
```

`AmbulanceGridlock.txt`:

```txt
[config]
Name = AmbulanceGridlock
Texture = event25.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(AmbulanceGridlock,-0.90,0.90);CreateGrudge(CareHomeOutbreak,-0.55,0.85);CreateGrudge(Health,-0.16,0.82);CreateGrudge(HealthcareDemand,0.14,0.82);CreateGrudge(_All_,-0.08,0.84);CreateGrudge(HospitalWinterCrisis,-0.40,0.80);

[influences]
0 = _random_,0.03,0.18
1 = HealthcareDemand,0+(0.34*x)
2 = Health,0.26-(0.26*x)
3 = _prereq_,_prereq_eu
```

`CareHomeOutbreak.txt`:

```txt
[config]
Name = CareHomeOutbreak
Texture = event25.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(CareHomeOutbreak,-0.90,0.90);CreateGrudge(AmbulanceGridlock,-0.55,0.85);CreateGrudge(Health,-0.14,0.82);CreateGrudge(Parents,-0.12,0.80);CreateGrudge(_All_,-0.08,0.84);CreateGrudge(HospitalWinterCrisis,-0.38,0.80);

[influences]
0 = _random_,0.03,0.18
1 = Health,0.28-(0.28*x)
2 = HealthcareDemand,0+(0.24*x)
3 = _prereq_,_prereq_eu
```

`CostOfLivingMarch.txt`:

```txt
[config]
Name = CostOfLivingMarch
Texture = event_flashcrash.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(CostOfLivingMarch,-0.93,0.90);CreateGrudge(CropFailureDrought,-0.40,0.78);CreateGrudge(HomelessCampCrisis,-0.40,0.78);CreateGrudge(EnergyPriceSpike,-0.35,0.78);CreateGrudge(Poor,-0.16,0.80);CreateGrudge(MiddleIncome,-0.14,0.80);CreateGrudge(_All_,-0.10,0.82);CreateGrudge(GDP,-0.08,0.84);

[influences]
0 = _random_,0.035,0.20
1 = PovertyRate,0+(0.30*x)
2 = FoodPrice,0+(0.26*x)
3 = Homelessness,0+(0.18*x)
4 = _prereq_,_prereq_eu
```

`EUFiscalWarning.txt`:

```txt
[config]
Name = EUFiscalWarning
Texture = event_flashcrash.png
GUISound = DM4_CoastalOilSpill.wav
OnImplement = CreateGrudge(EUFiscalWarning,-0.93,0.90);CreateGrudge(Debt,0.16,0.84);CreateGrudge(ForeignRelations,-0.12,0.82);CreateGrudge(Capitalist,-0.10,0.80);CreateGrudge(_All_,-0.08,0.84);CreateGrudge(CostOfLivingMarch,-0.35,0.78);

[influences]
0 = _random_,0.03,0.18
1 = Debt,0+(0.38*x)
2 = GDP,0.20-(0.20*x)
3 = ForeignRelations,0.16-(0.16*x)
4 = _prereq_,_prereq_eu
```

- [ ] **Step 2: Soft cross-cluster exclusion on heavy events**

Append these grudges to each heavy event’s `OnImplement` (keep existing grudges):

- Climate pair (`CropFailureDrought`, `CoastalFloodShock`): add  
  `CreateGrudge(HomelessCampCrisis,-0.45,0.80);CreateGrudge(LandlordExodus,-0.45,0.80);CreateGrudge(ReceptionCenterRiot,-0.45,0.80);CreateGrudge(SmugglerCorridorSpike,-0.45,0.80);`
- Housing pair: add climate + migration cluster Names with `-0.45,0.80`
- Migration pair: add climate + housing cluster Names with `-0.45,0.80`

- [ ] **Step 3: Append EN/IT strings for the 6 events**

EN:

```csv
#,PublicDataLeak,Public Data Leak,"A major leak of public data has damaged trust in digital government."
#,AutomationStrike,Automation Strike,"Workers are striking against rapid workplace automation."
#,AmbulanceGridlock,Ambulance Gridlock,"Emergency services are gridlocked; waiting times are surging."
#,CareHomeOutbreak,Care Home Outbreak,"An outbreak in care homes has exposed elder-care fragility."
#,CostOfLivingMarch,Cost of Living March,"Mass marches against living costs are shaking the government."
#,EUFiscalWarning,EU Fiscal Warning,"Brussels has issued a fiscal warning over debt and spending."
```

IT:

```csv
#,PublicDataLeak,"Fuga di dati pubblici","Una grossa fuga di dati pubblici ha colpito la fiducia nella PA digitale."
#,AutomationStrike,"Sciopero contro l'automazione","I lavoratori scioperano contro l'automazione rapida nei posti di lavoro."
#,AmbulanceGridlock,"Collasso delle ambulanze","Le emergenze sono intasate: i tempi di attesa esplodono."
#,CareHomeOutbreak,"Focolaio nelle RSA","Un focolaio nelle RSA ha mostrato la fragilita' della cura anziani."
#,CostOfLivingMarch,"Marcia del costo della vita","Marce di massa contro il caro vita scuotono il governo."
#,EUFiscalWarning,"Richiamo fiscale UE","Bruxelles ha emesso un richiamo fiscale su debito e spesa."
```

- [ ] **Step 4: Commit**

```powershell
git add ModernPressureEU/data/simulation/events ModernPressureEU/translations/English/events.csv ModernPressureEU/translations/Italian/events.csv
git commit -m "feat: add v2 light events and cross-cluster exclusion"
```

---

### Task 6: Config, install script, validate green, playtest checklist

**Files:**
- Modify: `ModernPressureEU/config.txt`
- Modify: `tools/install-to-documents.ps1`
- Modify: `docs/superpowers/plans/modern-pressure-eu-playtest.md`

**Interfaces:**
- Consumes: completed v2 content + Task 1 validator
- Produces: VALIDATE_OK + Documents deploy + checklist ready for human

- [ ] **Step 1: Update config description**

```ini
[config]
name = ModernPressureEU
path = C:\Users\nicho\Documents\My Games\Democracy4\mods\ModernPressureEU
guiname = Pressione Moderna UE
author = nicho
description = Pack UE v2: clima, casa, migrazione (deep) + tech/salute. Costi alti, crisi a ondate, effetti pesanti. 32 policy, 20 eventi. Gate _prereq_eu. Non e' un overhaul economico completo.
```

Mirror the same `description` inside `tools/install-to-documents.ps1` here-string.

- [ ] **Step 2: Run validator — expect PASS**

```powershell
powershell -NoProfile -File tools/validate-mod.ps1
```

Expected: `VALIDATE_OK`

- [ ] **Step 3: Deploy to Documents**

```powershell
powershell -NoProfile -File tools/install-to-documents.ps1
```

Expected: `INSTALLED=...ModernPressureEU`

- [ ] **Step 4: Extend playtest checklist**

Append to `docs/superpowers/plans/modern-pressure-eu-playtest.md`:

```markdown
## v2 checklist

- [ ] EU: 32 policies visible (spot-check new IDs in Economia/Welfare/Esteri/Servizi/Legge)
- [ ] IT strings readable on 3 new priority policies
- [ ] Non-EU: still 0 mod policies/events
- [ ] Long EU run: observe one heavy-cluster burst (2 related events close) OR note absence for retune
- [ ] Turn 30: no crash/softlock
```

- [ ] **Step 5: Commit**

```powershell
git add ModernPressureEU/config.txt tools/install-to-documents.ps1 docs/superpowers/plans/modern-pressure-eu-playtest.md
git commit -m "chore: ship v2 config deploy and playtest checklist"
```

---

## Spec coverage self-check

| Spec requirement | Task |
|------------------|------|
| 20 new policies exact IDs | 2, 3 |
| 12 new events exact Names | 4, 5 |
| `_prereq_eu` gate | 2–5 |
| IT+EN | 2–5 |
| Priority intensity vs tech/health | 2 vs 3 magnitudes; event chance Task 4 vs 5 |
| Burst + cross-cluster exclusion | 4, 5 |
| Icons | 2, 3 |
| validate 32/20 | 1, 6 |
| config/deploy/playtest | 6 |
| No mission overrides / no new prereq | Global — no task creates them |
| v1 IDs immutable | Global — only append |

## Placeholder / consistency notes

- Icon source filenames may differ per install; Task 2/3 include fallback to closest vanilla SVG with **exact destination names**.
- If `Equality` invalid as effect target, Task 3 says replace with `Liberal`.
- Burst uses mild sibling grudge (`-0.15,0.55`) not a chance boost field (Democracy 4 events lack a boost API); soft-suppress + high shared drivers approximate the wave. Retune after playtest if waves never land.
