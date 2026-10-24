$ErrorActionPreference = 'Stop'
$sourcePath = 'E:\sangsangXcode\模式题\国考判断推理原创模拟卷（一）-35题（含答案解析）.docx'
$pdfPath = 'E:\sangsangXcode\.work\guokao35\preview.pdf'
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
    if ($null -ne $wordDoc) { $wordDoc.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordDoc) }
    if ($null -ne $wordApp) { $wordApp.Quit(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) }
}
