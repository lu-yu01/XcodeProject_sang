$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$sourcePath = Join-Path $projectRoot '模式题\国考判断推理原创模拟卷（一）-35题（含答案解析）.docx'
$pdfPath = Join-Path $PSScriptRoot 'preview.pdf'
if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
    throw "未找到模拟卷：$sourcePath"
}
$wordApp = $null
$wordDoc = $null
try {
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $wordApp.AutomationSecurity = 3
    $wordDoc = $wordApp.Documents.Open($sourcePath, $false, $true, $false)
    $wordDoc.Repaginate()
    $pageCount = $wordDoc.ComputeStatistics(2)
    $wordDoc.ExportAsFixedFormat($pdfPath, 17)
    [pscustomobject]@{ Source=$sourcePath; Preview=$pdfPath; Pages=$pageCount } | ConvertTo-Json
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
