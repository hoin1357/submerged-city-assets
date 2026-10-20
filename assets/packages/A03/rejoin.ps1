$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$m = Get-Content -Raw -LiteralPath (Join-Path $root 'PARTS.json') | ConvertFrom-Json
$out = Join-Path $root $m.archive
if (Test-Path -LiteralPath $out) { throw 'Output already exists. Choose another folder; nothing overwritten.' }
foreach ($p in $m.parts) {
    $path = Join-Path $root $p.name
    if ((Get-Item -LiteralPath $path).Length -ne $p.bytes) { throw "Wrong size: $($p.name)" }
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant() -ne $p.sha256) { throw "Wrong SHA256: $($p.name)" }
}
$dest = [System.IO.File]::Open($out, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write)
try {
    foreach ($p in $m.parts) {
        $src = [System.IO.File]::OpenRead((Join-Path $root $p.name))
        try { $src.CopyTo($dest) } finally { $src.Dispose() }
    }
} finally { $dest.Dispose() }
if ((Get-Item -LiteralPath $out).Length -ne $m.bytes -or (Get-FileHash -Algorithm SHA256 -LiteralPath $out).Hash.ToLowerInvariant() -ne $m.sha256) { throw 'Joined archive failed verification. Do not extract it.' }
Write-Host "Verified: $($m.archive) $($m.sha256)"
Write-Host 'Extract this ZIP. Keep the Blender file and textures in their original relative locations.'
