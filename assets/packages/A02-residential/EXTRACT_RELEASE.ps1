#Requires -Version 5.1
<#
Built-in PowerShell/.NET verified extraction. Downloads/installs nothing.
Independent ZIP parts are extracted into unique temporary staging, then renamed once.
Use bundle/destination folders you control, without concurrent changes by other
processes. Path checks do not defend against hostile parent-directory replacement.
Different or incomplete existing output is never overwritten or merged.
This script has been statically reviewed, not executed in Windows here.
#>
[CmdletBinding()]
param(
    [string]$Bundle = $PSScriptRoot,
    [string]$Destination = '',
    [switch]$VerifyOnly,
    [string]$ExpectedInventorySha256 = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$Top = 'A02_residential_54_v2'
$Limit = 20000000L
$MaxMember = 536870912L
$MaxTotal = 4294967296L
$MaxIndex = 16777216L
$SupportNames = @('EXTRACT_RELEASE.py','EXTRACT_RELEASE.ps1','EXTRACT_RELEASE_WINDOWS.cmd','EXTRACT_ALL_README.txt','WINDOWS_README_KO.txt')

function Safe-Relative([string]$Name) {
    if ([string]::IsNullOrEmpty($Name) -or $Name.StartsWith('/') -or $Name.Contains('\')) { throw "Unsafe relative path: $Name" }
    foreach ($part in $Name.Split('/')) {
        if ($part -eq '' -or $part -eq '.' -or $part -eq '..' -or $part -match '[\x00-\x1F<>:"|?*]' -or $part.EndsWith('.') -or $part.EndsWith(' ')) { throw "Unsafe path component: $Name" }
        if ($part.Split('.')[0] -match '^(?i:CON|PRN|AUX|NUL|COM[1-9\u00B9\u00B2\u00B3]|LPT[1-9\u00B9\u00B2\u00B3])$') { throw "Reserved Windows path: $Name" }
    }
}
function No-Links([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    $current = $full
    while ($current) {
        if (-not [IO.File]::Exists($current) -and -not [IO.Directory]::Exists($current)) { throw "Path/parent does not exist: $current" }
        if (([IO.File]::GetAttributes($current) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Symlink/junction/reparse point forbidden: $current" }
        $parent = [IO.Directory]::GetParent($current)
        $current = if ($null -eq $parent) { $null } else { $parent.FullName }
    }
    return $full
}
function Safe-File([string]$Path) {
    $full = No-Links $Path
    if (-not [IO.File]::Exists($full) -or [IO.Directory]::Exists($full)) { throw "Not a regular file: $full" }
    return $full
}
function File-Hash([string]$Path) {
    $full = Safe-File $Path
    return (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Read-Index([string]$Path) {
    $full = Safe-File $Path
    if ((Get-Item -LiteralPath $full).Length -gt $MaxIndex) { throw "Index too large: $full" }
    return [IO.File]::ReadAllText($full, [Text.Encoding]::UTF8)
}
function New-Map { return [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal) }
function Check-Record($Row, [string]$Key = 'path') {
    $name = [string]$Row.$Key
    Safe-Relative $name
    if ($Row.bytes -isnot [int] -and $Row.bytes -isnot [long]) { throw "Invalid integer byte count: $name" }
    if ($Row.bytes -lt 0 -or $Row.bytes -gt $MaxMember -or [string]$Row.sha256 -cnotmatch '^[0-9a-f]{64}$') { throw "Invalid byte count/hash: $name" }
}
function Read-Sums([string]$Text) {
    $map = New-Map
    foreach ($line in ($Text -split '\r?\n')) {
        if ($line -eq '') { continue }
        $at = $line.IndexOf('  ')
        if ($at -ne 64) { throw 'Malformed checksum line' }
        $hash = $line.Substring(0,64); $name = $line.Substring(66)
        Safe-Relative $name
        if ($hash -cnotmatch '^[0-9a-f]{64}$' -or $map.ContainsKey($name)) { throw "Duplicate/invalid checksum entry: $name" }
        $map.Add($name,$hash)
    }
    return $map
}
function Require-SameSet($Actual, $Expected, [string]$Context) {
    $left = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $right = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($name in $Actual) { if (-not $left.Add([string]$name)) { throw "Duplicate item in $Context" } }
    foreach ($name in $Expected) { if (-not $right.Add([string]$name)) { throw "Duplicate expected item in $Context" } }
    if (-not $left.SetEquals($right)) { throw "Inventory set mismatch: $Context" }
}
function Find-Chunk([string]$Directory, $Row) {
    $name = [string]$Row.file
    if ($name.Contains('/')) { throw 'ZIP filename must not contain directories' }
    $stem = [IO.Path]::GetFileNameWithoutExtension($name)
    $pattern = '^' + [regex]::Escape($stem) + '(?: \([1-9][0-9]*\))?\.zip\z'
    $candidates = @(Get-ChildItem -LiteralPath $Directory -Force | Where-Object { $_.Name -cmatch $pattern } | Sort-Object @{Expression={ $_.Name -cne $name }},Name)
    foreach ($candidate in $candidates) {
        $path = Safe-File $candidate.FullName
        if ($candidate.Length -eq $Row.bytes -and (File-Hash $path) -ceq $Row.sha256) { return $path }
    }
    throw "Missing/corrupt ZIP: $name. Only the exact name or an exact numeric download suffix is accepted."
}
function Inspect-Entry($Entry, $Record) {
    Safe-Relative $Entry.FullName
    $attributes = [uint32]([int64]$Entry.ExternalAttributes -band 4294967295L)
    $kind = ($attributes -shr 16) -band 61440
    if ($Entry.Name -eq '' -or $kind -notin @(0,32768) -or ($attributes -band 1024) -ne 0) { throw "Link/device/directory entry forbidden: $($Entry.FullName)" }
    if ($Entry.Length -ne $Record.bytes -or $Entry.Length -gt $MaxMember) { throw "ZIP member size mismatch: $($Entry.FullName)" }
}
function Consume-Entry($Entry, $Record, $Output = $null, [bool]$Capture = $false) {
    if ($Capture -and $Record.bytes -gt $MaxIndex) { throw 'Inner index too large' }
    $source = $Entry.Open()
    $algorithm = [Security.Cryptography.SHA256]::Create()
    $memory = if ($Capture) { [IO.MemoryStream]::new() } else { $null }
    $buffer = New-Object byte[] 1048576
    $count = 0L
    try {
        while (($read = $source.Read($buffer,0,$buffer.Length)) -gt 0) {
            $count += $read
            if ($count -gt $Record.bytes) { throw "Inflated member exceeds inventory size: $($Entry.FullName)" }
            [void]$algorithm.TransformBlock($buffer,0,$read,$buffer,0)
            if ($null -ne $Output) { $Output.Write($buffer,0,$read) }
            if ($Capture) { $memory.Write($buffer,0,$read) }
        }
        [void]$algorithm.TransformFinalBlock((New-Object byte[] 0),0,0)
        $hash = ([BitConverter]::ToString($algorithm.Hash)).Replace('-','').ToLowerInvariant()
        if ($count -ne $Record.bytes -or $hash -cne $Record.sha256) { throw "Member hash/size mismatch: $($Entry.FullName)" }
        if ($Capture) { return [Text.Encoding]::UTF8.GetString($memory.ToArray()) }
    } finally {
        $source.Dispose(); $algorithm.Dispose()
        if ($null -ne $memory) { $memory.Dispose() }
    }
}
function Existing-Identical([string]$Target, $Members) {
    if (-not [IO.Directory]::Exists($Target) -and -not [IO.File]::Exists($Target)) { return $false }
    $targetFull = No-Links $Target
    if (-not [IO.Directory]::Exists($targetFull)) { throw 'Existing output is not a directory; refusing overwrite' }
    $expected = New-Map
    $directories = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($name in $Members.Keys) {
        $relative = $name.Substring($Top.Length+1); $expected.Add($relative,$Members[$name])
        $at = $relative.LastIndexOf('/')
        while ($at -gt 0) { [void]$directories.Add($relative.Substring(0,$at)); $at = $relative.LastIndexOf('/',$at-1) }
    }
    $actual = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $queue = [Collections.Generic.Queue[string]]::new(); $queue.Enqueue($targetFull)
    while ($queue.Count -gt 0) {
        $directory = $queue.Dequeue()
        foreach ($path in [IO.Directory]::EnumerateFileSystemEntries($directory)) {
            [void](No-Links $path)
            $relative = $path.Substring($targetFull.TrimEnd('\','/').Length+1).Replace('\','/')
            if ([IO.Directory]::Exists($path)) {
                if (-not $directories.Contains($relative)) { throw "Unexpected existing directory: $relative" }
                $queue.Enqueue($path); continue
            }
            [void](Safe-File $path)
            if (-not $expected.ContainsKey($relative) -or (Get-Item -LiteralPath $path).Length -ne $expected[$relative].bytes -or (File-Hash $path) -cne $expected[$relative].sha256) { throw "Existing file differs; refusing overwrite: $relative" }
            [void]$actual.Add($relative)
        }
    }
    Require-SameSet $actual $expected.Keys 'complete existing extraction (partial output is not merged)'
    return $true
}

$staging = $null; $lockStream = $null; $lockPath = $null
try {
    $Bundle = No-Links ($ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Bundle))
    if (-not [IO.Directory]::Exists($Bundle)) { throw 'Bundle must be a directory' }
    if ($null -eq [IO.Compression.ZipArchiveEntry].GetProperty('ExternalAttributes')) {
        throw 'Safe native extraction requires PowerShell 5.1 plus .NET Framework 4.7.2 or newer. Use the Python alternative or documented manual hash checks; no policy override or download is performed.'
    }
    $inventoryPath = Safe-File (Join-Path $Bundle 'chunk_inventory.json')
    if ((Get-Item -LiteralPath $inventoryPath).Length -gt $MaxIndex) { throw 'Inventory index too large' }
    $inventoryBytes = [IO.File]::ReadAllBytes($inventoryPath)
    if ($inventoryBytes.Length -gt $MaxIndex) { throw 'Inventory grew past the index limit' }
    $inventoryAlgorithm = [Security.Cryptography.SHA256]::Create()
    try { $inventoryHash = ([BitConverter]::ToString($inventoryAlgorithm.ComputeHash($inventoryBytes))).Replace('-','').ToLowerInvariant() }
    finally { $inventoryAlgorithm.Dispose() }
    $inventoryText = [Text.Encoding]::UTF8.GetString($inventoryBytes)
    if ($ExpectedInventorySha256 -and $inventoryHash -cne $ExpectedInventorySha256.ToLowerInvariant()) { throw 'Inventory does not match the supplied trusted SHA256' }
    $inventory = $inventoryText | ConvertFrom-Json
    if ($inventory.schema -cne 'residential54.zip-inventory.v1' -or $inventory.top_directory -cne $Top -or $inventory.byte_limit -ne $Limit) { throw 'Incorrect inventory identity or byte limit' }
    $cap = [long]$inventory.requested_byte_cap
    if ($cap -lt 1000000 -or $cap -gt $Limit) { throw 'Invalid ZIP byte cap' }
    $chunks = @($inventory.chunks)
    if ($chunks.Count -lt 1 -or $chunks.Count -gt 999) { throw 'Invalid part count' }
    $expectedNames = @(for ($i=1; $i -le $chunks.Count; $i++) { '{0}_part{1:00}_of{2:00}.zip' -f $Top,$i,$chunks.Count })
    Require-SameSet @($chunks | ForEach-Object { $_.file }) $expectedNames 'canonical ZIP sequence'
    $supportRows = @($inventory.support_files)
    Require-SameSet @($supportRows | ForEach-Object { $_.file }) $SupportNames 'support files'
    $sums = Read-Sums (Read-Index (Join-Path $Bundle 'SHA256SUMS.txt'))
    Require-SameSet $sums.Keys @($expectedNames + $SupportNames + @('chunk_inventory.json')) 'outer checksum list'
    if ($sums['chunk_inventory.json'] -cne $inventoryHash) { throw 'Outer inventory SHA256 mismatch' }
    foreach ($row in $supportRows) {
        Check-Record $row 'file'
        $path = Safe-File (Join-Path $Bundle $row.file)
        if ((Get-Item -LiteralPath $path).Length -ne $row.bytes -or (File-Hash $path) -cne $row.sha256 -or $sums[$row.file] -cne $row.sha256) { throw "Support-file hash/size mismatch: $($row.file)" }
    }
    $members = New-Map
    $folded = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $selection = [Collections.Generic.List[object]]::new()
    $total = 0L
    $directorySpellings = [Collections.Generic.Dictionary[string,string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($chunk in $chunks) {
        Check-Record $chunk 'file'
        if ($chunk.bytes -le 0 -or $chunk.bytes -gt $cap -or $sums[$chunk.file] -cne $chunk.sha256) { throw "Oversized/checksum-mismatched ZIP: $($chunk.file)" }
        $path = Find-Chunk $Bundle $chunk
        $current = New-Map
        if (@($chunk.members).Count -eq 0) { throw 'Empty ZIP member inventory' }
        foreach ($row in $chunk.members) {
            Check-Record $row
            $name = [string]$row.path
            if (-not $name.StartsWith($Top+'/',[StringComparison]::Ordinal) -or $name.Length -le $Top.Length+1) { throw 'Member outside required top directory' }
            if (-not $folded.Add($name)) { throw "Duplicate/case-colliding member: $name" }
            $at = $name.LastIndexOf('/')
            while ($at -gt 0) {
                $spelling = $name.Substring(0,$at)
                if ($directorySpellings.ContainsKey($spelling)) {
                    if ($directorySpellings[$spelling] -cne $spelling) { throw "Case-colliding directory spellings: $spelling" }
                } else { $directorySpellings.Add($spelling,$spelling) }
                $at = $name.LastIndexOf('/',$at-1)
            }
            $members.Add($name,$row); $current.Add($name,$row); $total += $row.bytes
            if ($total -gt $MaxTotal -or $members.Count -gt 100000) { throw 'Extraction exceeds safety bounds' }
        }
        $selection.Add([pscustomobject]@{ Chunk=$chunk; Path=$path; Members=$current })
    }
    Require-SameSet @($inventory.complete_member_paths) $members.Keys 'complete member list'
    foreach ($name in $members.Keys) {
        $at = $name.LastIndexOf('/')
        while ($at -gt 0) {
            if ($folded.Contains($name.Substring(0,$at))) { throw "File/directory prefix collision: $name" }
            $at = $name.LastIndexOf('/',$at-1)
        }
    }
    $inner = New-Map
    foreach ($part in $selection) {
        $zip = [IO.Compression.ZipFile]::OpenRead((Safe-File $part.Path))
        try {
            Require-SameSet @($zip.Entries | ForEach-Object { $_.FullName }) $part.Members.Keys 'actual ZIP members'
            foreach ($entry in $zip.Entries) {
                $row = $part.Members[$entry.FullName]; Inspect-Entry $entry $row
                $relative = $entry.FullName.Substring($Top.Length+1)
                $capture = $relative -cin @('STAGING_MANIFEST.json','FILE_SHA256SUMS.txt')
                $text = Consume-Entry $entry $row $null $capture
                if ($capture) { $inner.Add($relative,$text) }
            }
        } finally { $zip.Dispose() }
        if ((File-Hash $part.Path) -cne $part.Chunk.sha256) { throw 'ZIP changed during verification' }
    }
    Require-SameSet $inner.Keys @('STAGING_MANIFEST.json','FILE_SHA256SUMS.txt') 'required inner indexes'
    $stagingManifest = $inner['STAGING_MANIFEST.json'] | ConvertFrom-Json
    if ($stagingManifest.schema -cne 'residential54.staging-allowlist.v1' -or $stagingManifest.top_directory -cne $Top) { throw 'Incorrect inner staging-manifest identity' }
    Require-SameSet @($stagingManifest.generated_index_files) @('STAGING_MANIFEST.json','FILE_SHA256SUMS.txt') 'generated indexes'
    $stagedRows = New-Map
    foreach ($row in $stagingManifest.files) {
        Check-Record $row
        if ($stagedRows.ContainsKey($row.path)) { throw 'Duplicate staging-manifest path' }
        $stagedRows.Add($row.path,$row)
        $key = $Top+'/'+$row.path
        if (-not $members.ContainsKey($key) -or $members[$key].sha256 -cne $row.sha256 -or $members[$key].bytes -ne $row.bytes) { throw "Staging-manifest hash/size mismatch: $($row.path)" }
    }
    $allowed = @($stagedRows.Keys | ForEach-Object { $Top+'/'+$_ }) + @($stagingManifest.generated_index_files | ForEach-Object { $Top+'/'+$_ })
    Require-SameSet $allowed $members.Keys 'explicit staging allowlist'
    $innerSums = Read-Sums $inner['FILE_SHA256SUMS.txt']
    Require-SameSet $innerSums.Keys @(@($stagedRows.Keys) + @('STAGING_MANIFEST.json')) 'inner checksum list'
    foreach ($relative in $innerSums.Keys) {
        if ($members[$Top+'/'+$relative].sha256 -cne $innerSums[$relative]) { throw "Inner manifest checksum mismatch: $relative" }
    }
    if ($VerifyOnly) {
        Write-Host "VERIFIED ONLY: $($chunks.Count) ZIP parts; $($members.Count) files; no extraction performed."
        Write-Host "Inventory SHA256: $inventoryHash"
        exit 0
    }
    if (-not $Destination) { $Destination = $Bundle }
    $Destination = No-Links ($ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination))
    if (-not [IO.Directory]::Exists($Destination)) { throw 'Destination parent must already exist' }
    $target = Join-Path $Destination $Top
    if (Existing-Identical $target $members) { Write-Host "Already complete and identical; no changes: $target"; exit 0 }
    $lockPath = Join-Path $Destination ('.'+$Top+'.extract.lock')
    $lockStream = [IO.File]::Open($lockPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    if ([IO.Directory]::Exists($target) -or [IO.File]::Exists($target)) { throw 'Output appeared during validation; refusing overwrite' }
    $staging = Join-Path $Destination ('.'+$Top+'.extract-staging-'+[Guid]::NewGuid().ToString('N'))
    [void][IO.Directory]::CreateDirectory($staging)
    $stagedTop = Join-Path $staging $Top
    [void][IO.Directory]::CreateDirectory($stagedTop)
    foreach ($part in $selection) {
        if ((File-Hash $part.Path) -cne $part.Chunk.sha256) { throw 'ZIP changed before extraction' }
        $zip = [IO.Compression.ZipFile]::OpenRead((Safe-File $part.Path))
        try {
            Require-SameSet @($zip.Entries | ForEach-Object { $_.FullName }) $part.Members.Keys 'ZIP contents before extraction'
            foreach ($entry in $zip.Entries) {
                $row = $part.Members[$entry.FullName]; Inspect-Entry $entry $row
                $relative = $entry.FullName.Substring($Top.Length+1); Safe-Relative $relative
                $outputPath = Join-Path $stagedTop $relative.Replace('/',[IO.Path]::DirectorySeparatorChar)
                [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($outputPath))
                $output = [IO.File]::Open($outputPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
                try { Consume-Entry $entry $row $output $false } finally { $output.Dispose() }
            }
        } finally { $zip.Dispose() }
        if ((File-Hash $part.Path) -cne $part.Chunk.sha256) { throw 'ZIP changed during extraction' }
    }
    if (-not (Existing-Identical $stagedTop $members)) { throw 'Staged output is incomplete' }
    [void](No-Links $Destination)
    if ([IO.Directory]::Exists($target) -or [IO.File]::Exists($target)) { throw 'Output appeared during extraction; refusing overwrite' }
    [IO.Directory]::Move($stagedTop,$target)
    Write-Host "EXTRACTED AND VERIFIED: $($chunks.Count) ZIP parts; $($members.Count) files."
    Write-Host "Directory: $target"
    Write-Host "Inventory SHA256: $inventoryHash"
} catch {
    [Console]::Error.WriteLine('SAFE EXTRACTION BLOCKED: '+$_.Exception.Message)
    exit 2
} finally {
    if ($null -ne $staging -and [IO.Directory]::Exists($staging)) { [IO.Directory]::Delete($staging,$true) }
    if ($null -ne $lockStream) { $lockStream.Dispose(); [IO.File]::Delete($lockPath) }
}
