param(
  [string]$AlbumMatch = "Please_Please_Me",
  [int]$Count = 5,
  [string]$ApiBase = "http://localhost:8000",
  [string]$Root = "$PSScriptRoot/../References/Beatles-Chords"
)

$ErrorActionPreference = 'Stop'

Write-Host "Album filter:" $AlbumMatch
Write-Host "API:" $ApiBase
Write-Host "Root:" $Root

# Pick first N files matching album
$files = Get-ChildItem -Path $Root -Filter *.jcrd.json |
  Where-Object { $_.Name -like "*${AlbumMatch}*" } |
  Sort-Object Name |
  Select-Object -First $Count

if (-not $files -or $files.Count -eq 0) {
  Write-Host "No files matched." -ForegroundColor Yellow
  exit 1
}

$ids = @()
foreach ($f in $files) {
  try {
    Write-Host "Importing" $f.Name
    $j = Get-Content -Raw -Path $f.FullName | ConvertFrom-Json
    $title = $j.metadata.title
    $artist = $j.metadata.artist
    $payload = @{ jcrd = $j; lyrics = @{ lines = @() }; include_lyrics = $true; title = $title; artist = $artist }
    $body = $payload | ConvertTo-Json -Depth 50
    $res = Invoke-RestMethod -Method Post -Uri "$ApiBase/combine/jcrd-lyrics?save=true" -ContentType 'application/json' -Body $body
    if ($res.song -and $res.song.id) {
      $ids += $res.song.id
      Write-Host ("Saved #" + $res.song.id)
    } else {
      Write-Host "Saved (no id)" -ForegroundColor Yellow
    }
    Start-Sleep -Milliseconds 150
  } catch {
    Write-Warning ("Failed: " + $f.Name + " -> " + $_.Exception.Message)
  }
}

if ($ids.Count -eq 0) {
  Write-Host "No songs saved." -ForegroundColor Yellow
  exit 1
}

Write-Host "Imported IDs:" ($ids -join ', ')

# Print proof: BPM/timeSig from /doc, and bpmDefault/timeSig/sections from /timeline
foreach ($id in $ids) {
  try {
    $doc = Invoke-RestMethod -Method Get -Uri "$ApiBase/v1/songs/$id/doc"
    $tl = Invoke-RestMethod -Method Get -Uri "$ApiBase/v1/songs/$id/timeline"
  $bpm = $doc.bpm
  $ts = $doc.timeSignature
  $bpmDef = $tl.timeline.bpmDefault
  $tsMark = $tl.timeline.timeSigMap | Select-Object -First 1
  $tsDef = if ($tsMark) { ($tsMark.num.ToString() + '/' + $tsMark.den.ToString()) } else { '' }
    $sec = ($tl.timeline.sections | Select-Object -First 3 | ForEach-Object { $_.name }) -join ', '
    Write-Host ("Song " + $id + ": doc(bpm=" + $bpm + ", ts=" + $ts + ") | timeline(bpmDefault=" + $bpmDef + ", ts=" + $tsDef + ") | sections=" + $sec)
  } catch {
    Write-Warning ("Inspect failed for #${id}: " + $_.Exception.Message)
  }
}
