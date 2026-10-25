$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$sourcePath = Join-Path $projectRoot '模式题\国考判断推理原创模拟卷（二）-2026行政执法-35题（含答案解析）.docx'
$pdfPath = Join-Path $PSScriptRoot 'preview.pdf'
if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
    throw "未找到模拟卷：$sourcePath"
}
$wordApp = $null
$wordDoc = $null
try {
    Write-Output 'Starting Word'
    $wordApp = New-Object -ComObject Word.Application
    Write-Output 'Word started'
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $wordApp.AutomationSecurity = 3
    Write-Output 'Opening document'
    $wordDoc = $wordApp.Documents.Open($sourcePath, $false, $true, $false)
    Write-Output 'Document opened; exporting PDF'
    $wordDoc.ExportAsFixedFormat($pdfPath, 17)
    Write-Output 'PDF exported'
    [pscustomobject]@{ Source=$sourcePath; Preview=$pdfPath } | ConvertTo-Json
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
