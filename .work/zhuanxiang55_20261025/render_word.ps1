param([string]$SourcePath, [string]$PdfPath)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
if (-not $SourcePath) { $SourcePath = Join-Path $projectRoot '模式题\国考图形与逻辑专项练习-55题（含答案解析）.docx' }
if (-not $PdfPath) { $PdfPath = Join-Path $PSScriptRoot 'preview.pdf' }
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
