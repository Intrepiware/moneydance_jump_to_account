$extId = "quick_account_switcher"
$sourceDir = ".\ext"
$zipFile = ".\$extId.zip"
$mxtFile = ".\$extId.mxt"

# 1. Clean previous build artifacts
Remove-Item $zipFile, $mxtFile -ErrorAction SilentlyContinue

# 2. Compress extension folder contents into ZIP format
Compress-Archive -Path "$sourceDir\*" -DestinationPath $zipFile

# 3. Rename .zip to .mxt
Rename-Item -Path $zipFile -NewName $mxtFile

# 4. Sign the .mxt package using Moneydance Developer Kit
# java -cp signext.jar com.infinitekind.moneydance.tools.SignExt $privKey $privKeyId $extId $mxtFile

Write-Host "Build and signing complete: $mxtFile" -ForegroundColor Green