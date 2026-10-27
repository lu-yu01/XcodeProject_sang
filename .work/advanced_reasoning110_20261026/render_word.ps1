param([Parameter(Mandatory=$true)][string]$SourcePath, [Parameter(Mandatory=$true)][string]$PdfPath)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) { throw "Missing document: $SourcePath" }
$wordApp = $null
$wordDoc = $null
try {
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $wordApp.AutomationSecurity = 3
    $wordDoc = $wordApp.Documents.Open($SourcePath, $false, $true, $false)
    $wordDoc.ExportAsFixedFormat($PdfPath, 17)
    [pscustomobject]@{ Source=$SourcePath; Preview=$PdfPath } | ConvertTo-Json
} finally {
    if ($null -ne $wordDoc) {
        $wordDoc.Saved = $true
        $wordDoc.Close()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordDoc)
    }
    if ($null -ne $wordApp) {
        $wordApp.Quit()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp)
    }
}
