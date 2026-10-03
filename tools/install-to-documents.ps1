$ErrorActionPreference = "Stop"
$src = (Resolve-Path "ModernPressureEU").Path
$destParent = Join-Path $env:USERPROFILE "Documents\My Games\Democracy4\mods"
if (-not (Test-Path (Split-Path $destParent -Parent))) {
  $alt = Join-Path $env:USERPROFILE "Documents\My Games\democracy4\mods"
  if (Test-Path (Split-Path $alt -Parent)) { $destParent = $alt }
}
New-Item -ItemType Directory -Force -Path $destParent | Out-Null
$dest = Join-Path $destParent "ModernPressureEU"
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Copy-Item $src $dest -Recurse
$cfg = @"
[config]
name = ModernPressureEU
path = $dest
guiname = Modern Pressure EU
author = JustNever_
description = EU pressure pack (v2): climate, housing, migration, tech/AI, health. 32 policies, 20 crisis events, hard costs, burst crises. Additive content for EU missions (_prereq_eu). Not a full economy overhaul. Source: https://github.com/Never-lab/modern-pressure-eu
"@
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText((Join-Path $dest "config.txt"), $cfg, $utf8NoBom)
# Ensure workshop preview assets are present after copy
foreach ($img in @("preview.jpg", "icon.jpg")) {
  $p = Join-Path $dest $img
  if (-not (Test-Path $p)) { Write-Warning "missing $img in install output" }
}
Write-Output "INSTALLED=$dest"
