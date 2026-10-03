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
