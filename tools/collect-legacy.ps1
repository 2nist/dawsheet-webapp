param(
  [string]$SourceRoot = 'H:\My Drive\dawsheetextractor\DAWSheet-Project',
  [string]$DestRepo   = 'C:\Users\CraftAuto-Sales\dawsheet\webapp',
  [switch]$Copy,
  [switch]$IncludeLarge,
  [int]$MaxSizeMB = 20
)

$ErrorActionPreference = 'Stop'

# Dest structure
$LegacyRoot = Join-Path $DestRepo 'legacy'
$Folders = @(
  'docs','code-snippets',
  'samples\json','samples\pro','samples\midi','samples\mp3','samples\txt',
  'postman','notebooks'
) | ForEach-Object { Join-Path $LegacyRoot $_ }
$Folders | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }

# Ignore dirs
$IgnoreDirs = @('\\.git\\','node_modules','__pycache__','\\.venv','\bdist\b','\bbuild\b','\\.pytest_cache')

function Test-IgnoredPath($p) {
  foreach($pat in $IgnoreDirs){ if ($p -ireplace '\\','\\' -match $pat){ return $true } }
  return $false
}

$Report = New-Object System.Collections.Generic.List[object]
$SeenPaths = New-Object System.Collections.Generic.HashSet[string]

function Add-Candidate {
  param(
    [string]$Path,[string]$Category,[string]$Reason,[string]$DestSub
  )
  $fi = Get-Item -LiteralPath $Path -ErrorAction SilentlyContinue
  if(-not $fi){ return }
  # De-dup by absolute path (avoid multiple entries for the same file)
  if($SeenPaths.Contains($fi.FullName)) { return }
  $sizeMB = [Math]::Round(($fi.Length/1MB),2)
  $TooLarge = -not $IncludeLarge -and $sizeMB -gt $MaxSizeMB
  $rec = [pscustomobject]@{
    Path = $fi.FullName
    SizeMB = $sizeMB
    Category = $Category
    Reason = $Reason
    SuggestedDest = (Join-Path $LegacyRoot $DestSub)
    WillCopy = if($Copy -and -not $TooLarge){ 'Yes' } elseif($TooLarge){ 'Skip(large)' } else { 'No' }
  }
  $Report.Add($rec) | Out-Null
  $null = $SeenPaths.Add($fi.FullName)
}

Write-Host "Scanning $SourceRoot ..." -ForegroundColor Cyan

# Helper: get files by recursive patterns (PowerShell 7 '**' support)
function Get-MatchedFiles {
  param([string[]]$Patterns)
  $files = @()
  foreach($pat in $Patterns){
    $p = Join-Path $SourceRoot $pat
    $files += Get-ChildItem -Path $p -Recurse -File -ErrorAction SilentlyContinue
  }
  $files | Where-Object { -not (Test-IgnoredPath $_.FullName) }
}

# 1) Docs (md/txt with relevant keywords)
$docKeywords = 'chord|parser|import|midi|lyrics|chordpro|section|timeline|alembic|schema'
Get-MatchedFiles -Patterns @('**/*.md','**/*.txt') |
  ForEach-Object {
    $hit = Select-String -Path $_.FullName -Pattern $docKeywords -SimpleMatch:$false -Quiet -ErrorAction SilentlyContinue
    if($hit){ Add-Candidate -Path $_.FullName -Category 'doc' -Reason 'keyword-hit' -DestSub 'docs' }
  }

# 2) Code snippets (python) by filename keywords
Get-MatchedFiles -Patterns @('**/*.py') |
  Where-Object { $_.Name -match 'parser|analy[sz]e|import|midi|lyrics|chord' } |
  ForEach-Object { Add-Candidate -Path $_.FullName -Category 'code' -Reason 'filename-match' -DestSub 'code-snippets' }

# 3) Samples: JSON likely song payloads
Get-MatchedFiles -Patterns @('**/*.json') |
  ForEach-Object {
    $content = $null
    try { $content = Get-Content -LiteralPath $_.FullName -Raw -ErrorAction Stop }
    catch { $content = $null }
    if($content -and ($content -match '"songs"' -or ($content -match '"title"' -and $content -match '"content"'))){
      Add-Candidate -Path $_.FullName -Category 'sample-json' -Reason 'json-keys' -DestSub 'samples\json'
    }
  }

# 4) Samples: ChordPro / text
Get-MatchedFiles -Patterns @('**/*.pro','**/*.chordpro','**/*.song') |
  ForEach-Object { Add-Candidate -Path $_.FullName -Category 'sample-pro' -Reason 'chordpro' -DestSub 'samples\pro' }
Get-MatchedFiles -Patterns @('**/*.txt','**/*.md') |
  ForEach-Object { Add-Candidate -Path $_.FullName -Category 'sample-text' -Reason 'lyrics/text' -DestSub 'samples\txt' }

# 5) MIDI
Get-MatchedFiles -Patterns @('**/*.mid','**/*.midi') |
  ForEach-Object { Add-Candidate -Path $_.FullName -Category 'sample-midi' -Reason 'midi' -DestSub 'samples\midi' }

# 6) MP3 (opt-in for large)
Get-MatchedFiles -Patterns @('**/*.mp3') |
  ForEach-Object { Add-Candidate -Path $_.FullName -Category 'sample-mp3' -Reason 'mp3' -DestSub 'samples\mp3' }

# 7) Postman collections
Get-MatchedFiles -Patterns @('**/*postman*collection*.json') |
  ForEach-Object { Add-Candidate -Path $_.FullName -Category 'postman' -Reason 'postman-collection' -DestSub 'postman' }

# 8) Notebooks
Get-MatchedFiles -Patterns @('**/*.ipynb') |
  ForEach-Object { Add-Candidate -Path $_.FullName -Category 'notebook' -Reason 'ipynb' -DestSub 'notebooks' }

# Save report
$csv = Join-Path $LegacyRoot 'collection-report.csv'
$json = Join-Path $LegacyRoot 'collection-report.json'
$Report | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8
$Report | ConvertTo-Json -Depth 6 | Out-File -FilePath $json -Encoding UTF8

Write-Host "Report written to:" -ForegroundColor Green
Write-Host "  $csv"
Write-Host "  $json"

# Copy phase
if($Copy){
  Write-Host "Copying curated files..." -ForegroundColor Cyan
  $copied = 0
  foreach($r in $Report){
    if($r.WillCopy -ne 'Yes'){ continue }
    $destDir = $r.SuggestedDest
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    try {
      Copy-Item -Force -LiteralPath $r.Path -Destination $destDir
      $copied++
    } catch {
      Write-Warning "Failed to copy: $($r.Path) -> $destDir ($($_.Exception.Message))"
    }
  }
  Write-Host "Copied $copied files into $LegacyRoot" -ForegroundColor Green
  Write-Host "Tip: Consider 'git lfs track "*.mp3"' before committing large audio." -ForegroundColor Yellow
}
