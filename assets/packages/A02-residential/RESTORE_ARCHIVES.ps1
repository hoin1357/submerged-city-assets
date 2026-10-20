$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$m = Get-Content -Raw -LiteralPath (Join-Path $root 'BACKUP_PARTS.json') | ConvertFrom-Json
foreach ($a in $m.archives) {
    $out = Join-Path $root $a.archive
    if (Test-Path -LiteralPath $out) {
        if ((Get-Item -LiteralPath $out).Length -eq $a.bytes -and (Get-FileHash -Algorithm SHA256 -LiteralPath $out).Hash.ToLowerInvariant() -eq $a.sha256) { Write-Host "Already verified: $($a.archive)"; continue }
        throw "Existing output does not match. Use a clean folder: $($a.archive)"
    }
    foreach ($p in $a.parts) {
        $path = Join-Path $root $p.name
        if ((Get-Item -LiteralPath $path).Length -ne $p.bytes -or (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant() -ne $p.sha256) { throw "Part verification failed: $($p.name)" }
    }
    $dest = [System.IO.File]::Open($out, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write)
    try { foreach ($p in $a.parts) {
        $src = [System.IO.File]::OpenRead((Join-Path $root $p.name))
        try { $src.CopyTo($dest) } finally { $src.Dispose() }
    } } finally { $dest.Dispose() }
    if ((Get-Item -LiteralPath $out).Length -ne $a.bytes -or (Get-FileHash -Algorithm SHA256 -LiteralPath $out).Hash.ToLowerInvariant() -ne $a.sha256) { throw "Joined ZIP failed verification: $($a.archive)" }
    Write-Host "Verified: $($a.archive) $($a.sha256)"
}
Write-Host 'All archive bytes verified. Follow the delivery extraction/install instructions next.'
