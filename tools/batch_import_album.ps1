param(
  [string]$AlbumMatch = "Rubber_Soul",
  [string]$ApiBase = "http://localhost:8000",
  [string]$Root = "$PSScriptRoot/../References/Beatles-Chords"
)

Write-Host "Album match:" $AlbumMatch
$files = Get-ChildItem -Path $Root -Filter *.jcrd.json | Where-Object { $_.Name -like "*${AlbumMatch}*" } | Sort-Object Name
if (-not $files -or $files.Count -eq 0) {
  Write-Host "No files matched." -ForegroundColor Yellow
  exit 1
}

$imported = 0
$errors = @()

foreach ($f in $files) {
  try {
    Write-Host "Importing" $f.Name
    # Read JSON and post through /combine/jcrd-lyrics with include_lyrics=true
    $j = Get-Content -Raw -Path $f.FullName | ConvertFrom-Json
    $title = ($j.metadata.title) | ForEach-Object { if ($_ -is [string]) { $_ } else { "Untitled" } }
    $artist = ($j.metadata.artist) | ForEach-Object { if ($_ -is [string]) { $_ } else { "" } }
    $payload = @{ jcrd = $j; lyrics = @{ lines = @() }; include_lyrics = $true; title = $title; artist = $artist }
    $body = $payload | ConvertTo-Json -Depth 50
    $res = Invoke-RestMethod -Method Post -Uri "$ApiBase/combine/jcrd-lyrics?save=true" -ContentType 'application/json' -Body $body
    if ($res.song -and $res.song.id) {
      Write-Host "Saved song #" $res.song.id
      $imported++
    } else {
      Write-Host "Saved (no id returned)" -ForegroundColor Yellow
    }
    Start-Sleep -Milliseconds 250
  } catch {
    $msg = $_.Exception.Message
    Write-Warning "Failed: $($f.Name) -> $msg"
    $errors += "$($f.Name): $msg"
  }
}

Write-Host "Imported:" $imported "file(s)."
if ($errors.Count -gt 0) {
  Write-Host "Errors:" -ForegroundColor Yellow
  $errors | ForEach-Object { Write-Host " - $_" }
}
