param(
  [string]$GamePath = (Get-Content "reference/game_path.txt" -Raw).Trim(),
  [string]$ModRoot = "ModernPressureEU",
  [string[]]$EuIds = @("germany", "france", "italy", "spain", "greece", "ireland", "poland")
)
$ErrorActionPreference = "Stop"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$roots = @(
  (Join-Path $GamePath "data\missions"),
  (Join-Path $GamePath "countrypack\data\missions")
) | Where-Object { Test-Path $_ }

$found = @()
foreach ($id in $EuIds) {
  $match = $null
  foreach ($missionsRoot in $roots) {
    $match = Get-ChildItem $missionsRoot -Directory | Where-Object { $_.Name -ieq $id } | Select-Object -First 1
    if ($match) { break }
  }
  if (-not $match) { Write-Warning "Skip missing mission $id"; continue }

  $srcTxt = Get-ChildItem $match.FullName -Filter "*.txt" | Where-Object { $_.BaseName -ieq $match.Name } | Select-Object -First 1
  if (-not $srcTxt) { $srcTxt = Get-ChildItem $match.FullName -Filter "*.txt" | Select-Object -First 1 }
  if (-not $srcTxt) { throw "No txt in $($match.FullName)" }

  # Always re-copy from live game/DLC so updates don't leave a stale broken snapshot.
  $destDir = Join-Path $ModRoot "data\missions\$($match.Name)"
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null
  $dest = Join-Path $destDir $srcTxt.Name
  $text = [System.IO.File]::ReadAllText($srcTxt.FullName, $utf8NoBom)
  if ($text -notmatch '(?im)^_prereq_mod_eu\s*=') {
    if ($text -notmatch '(?im)\[policies\]') { throw "$($match.Name) missing [policies] section" }
    $text = [regex]::Replace($text, '(?im)(\[policies\]\s*)', "`$1`r`n_prereq_mod_eu = 1`r`n", 1)
  }
  [System.IO.File]::WriteAllText($dest, $text, $utf8NoBom)
  $found += $match.Name
}

if ($found.Count -lt 1) { throw "No EU missions injected" }
[System.IO.File]::WriteAllText("reference/eu_missions_injected.txt", "Injected: $($found -join ', ')", $utf8NoBom)
Write-Output "Injected: $($found -join ', ')"
