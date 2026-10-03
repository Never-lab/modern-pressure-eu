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
$en = Get-Content "$root/translations/English/policies.csv"
$it = Get-Content "$root/translations/Italian/policies.csv"
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

foreach ($id in $ids) {
  $icon = Join-Path $root ("data/svg/icons_{0}.svg" -f $id.ToLower())
  if (-not (Test-Path $icon)) { throw "missing icon $icon" }
}
Write-Output "VALIDATE_OK"
