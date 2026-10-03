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
guiname = Pressione Moderna UE
author = nicho
description = Pack UE v2: clima, casa, migrazione (deep) + tech/salute. Costi alti, crisi a ondate, effetti pesanti. 32 policy, 20 eventi. Gate _prereq_eu. Non e' un overhaul economico completo.
"@
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText((Join-Path $dest "config.txt"), $cfg, $utf8NoBom)
Write-Output "INSTALLED=$dest"
