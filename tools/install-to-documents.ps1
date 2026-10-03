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
author = nicho
description = EU pressure pack: climate, housing, tech/AI, migration, health. Hard costs, slow payoffs, serious crises. Additive content + EU mission flag. Not a full economy overhaul.
"@
Set-Content -Path (Join-Path $dest "config.txt") -Value $cfg -Encoding utf8
Write-Output "INSTALLED=$dest"
