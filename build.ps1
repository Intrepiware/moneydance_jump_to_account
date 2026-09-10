$ErrorActionPreference = "Stop"
$extId = "quick_account_switcher"
$sourceDir = Join-Path $PSScriptRoot "ext"
$mxtFile = Join-Path $PSScriptRoot "$extId.mxt"

foreach ($requiredFile in @("meta_info.dict", "script_info.dict", "$extId.py")) {
    if (-not (Test-Path -LiteralPath (Join-Path $sourceDir $requiredFile) -PathType Leaf)) {
        throw "Missing required extension file: $requiredFile"
    }
}

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

# Write explicit JAR entry names so paths use forward slashes on Windows too.
$stream = [System.IO.File]::Open($mxtFile, [System.IO.FileMode]::Create)
try {
    $archive = [System.IO.Compression.ZipArchive]::new($stream, [System.IO.Compression.ZipArchiveMode]::Create)
    try {
        foreach ($file in Get-ChildItem -LiteralPath $sourceDir -File -Recurse) {
            $entryName = $file.FullName.Substring($sourceDir.Length + 1).Replace('\', '/')
            if ($entryName -eq "meta_info.dict") {
                $entryName = "com/moneydance/modules/features/$extId/meta_info.dict"
            }
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                $archive, $file.FullName, $entryName) | Out-Null
        }
    } finally {
        $archive.Dispose()
    }
} finally {
    $stream.Dispose()
}

Write-Host "Build complete (unsigned): $mxtFile" -ForegroundColor Green
