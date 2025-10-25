$ErrorActionPreference = 'Stop'
$dir = 'c:\MAIN-PROJECT\health-data-exchange'
$target = Join-Path $dir 'main_updated.tex'
$backups = Get-ChildItem -File -Path $dir -Filter 'main_updated.tex.bak.*' | Sort-Object LastWriteTime -Descending
if (-not $backups -or $backups.Count -eq 0) {
  Write-Error 'No backup files found.'
  exit 1
}
$latest = $backups[0]
Copy-Item -Path $latest.FullName -Destination $target -Force
Write-Output ("Restored {0} from backup: {1}" -f $target, $latest.Name)
