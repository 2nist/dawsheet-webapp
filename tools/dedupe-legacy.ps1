param(
  [string]$LegacyRoot = 'h:\My Drive\dawsheetextractor\DAWSheet-Project\webapp\legacy'
)

$ErrorActionPreference = 'Stop'
$Trash = Join-Path $LegacyRoot '_trash_dupes'
New-Item -ItemType Directory -Force -Path $Trash | Out-Null

function Get-FileHashSafe($p){
  try { return (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash }
  catch { return $null }
}

$map = @{}
$dupes = New-Object System.Collections.Generic.List[object]

Get-ChildItem -LiteralPath $LegacyRoot -Recurse -File |
  Where-Object { $_.FullName -notmatch '\\_trash_' } |
  ForEach-Object {
    $h = Get-FileHashSafe $_.FullName
    if(-not $h){ return }
    if($map.ContainsKey($h)){
      # duplicate; move to trash, keep first occurrence
      $rel = $_.FullName.Substring($LegacyRoot.Length).TrimStart('\\')
      $dest = Join-Path $Trash $rel
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null
      Move-Item -Force -LiteralPath $_.FullName -Destination $dest
      $dupes.Add([pscustomobject]@{ Path=$_.FullName; Hash=$h; MovedTo=$dest }) | Out-Null
    } else {
      $map[$h] = $_.FullName
    }
  }

$dupeReport = Join-Path $LegacyRoot 'duplicates.csv'
$dupes | Export-Csv -NoTypeInformation -Path $dupeReport -Encoding UTF8
Write-Host "Duplicates moved: $($dupes.Count)" -ForegroundColor Yellow
Write-Host "Details: $dupeReport"
