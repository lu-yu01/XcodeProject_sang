$ErrorActionPreference = 'Stop'
$project = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$manifest = Join-Path $PSScriptRoot 'corpus_audit\manifest.jsonl'
$output = Join-Path $PSScriptRoot 'corpus_audit\xls_question_metadata.jsonl'
$items = Get-Content -LiteralPath $manifest -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json }
$targets = @($items | Where-Object {
    $_.extension -eq '.xls' -and (
        $_.path -match '/公务员笔试-行测真题试卷/' -or
        $_.path -match '/事业单位笔试-职测真题试卷/' -or
        $_.path -match '/自建试卷/'
    )
})
$writer = [System.IO.StreamWriter]::new($output, $false, [System.Text.UTF8Encoding]::new($false))
$app = $null
$success = 0
$failed = 0
try {
    $app = New-Object -ComObject Excel.Application
    $app.Visible = $false
    $app.DisplayAlerts = $false
    $app.AutomationSecurity = 3
    $app.EnableEvents = $false
    $app.AskToUpdateLinks = $false
    foreach ($item in $targets) {
        $book = $null
        $sheet = $null
        $used = $null
        $record = [ordered]@{ path = $item.path; questions = @() }
        try {
            $file = Join-Path $project ($item.path.Replace('/', '\'))
            $book = $app.Workbooks.Open($file, 0, $true)
            $sheet = $book.Worksheets.Item(1)
            $used = $sheet.UsedRange
            $values = $used.Value2
            if (-not ($values -is [Array]) -or $values.Rank -ne 2) {
                throw 'Unexpected worksheet shape'
            }
            $firstRow = $values.GetLowerBound(0)
            $lastRow = $values.GetUpperBound(0)
            $firstCol = $values.GetLowerBound(1)
            $lastCol = $values.GetUpperBound(1)
            $record.headers = @($firstCol..$lastCol | ForEach-Object { [string]$values.GetValue($firstRow, $_) })
            $record.rows = $lastRow - $firstRow
            $record.sheet = [string]$sheet.Name
            $noCol = [Array]::IndexOf($record.headers, '题序') + $firstCol
            $pointCol = [Array]::IndexOf($record.headers, '知识点') + $firstCol
            $answerCol = [Array]::IndexOf($record.headers, '答案') + $firstCol
            if ($noCol -lt $firstCol -or $pointCol -lt $firstCol -or $answerCol -lt $firstCol) {
                throw 'Missing 题序/知识点/答案 columns'
            }
            $questions = [System.Collections.Generic.List[object]]::new()
            for ($row = $firstRow + 1; $row -le $lastRow; $row++) {
                $number = $values.GetValue($row, $noCol)
                $point = $values.GetValue($row, $pointCol)
                $answer = $values.GetValue($row, $answerCol)
                if ($null -eq $number -and $null -eq $point -and $null -eq $answer) { continue }
                $questions.Add([ordered]@{ no = $number; point = [string]$point; answer = [string]$answer })
            }
            $record.questions = $questions.ToArray()
            $success++
        } catch {
            $record.error = $_.Exception.Message
            $failed++
        } finally {
            if ($null -ne $book) { $book.Close($false) }
            if ($null -ne $used) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($used) }
            if ($null -ne $sheet) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($sheet) }
            if ($null -ne $book) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($book) }
        }
        $writer.WriteLine(($record | ConvertTo-Json -Depth 6 -Compress))
        if (($success + $failed) % 50 -eq 0) {
            $writer.Flush()
            Write-Output "Scanned $($success + $failed)/$($targets.Count); OK $success; errors $failed"
            [GC]::Collect()
            [GC]::WaitForPendingFinalizers()
        }
    }
    $writer.Flush()
    Write-Output "Completed $($targets.Count); OK $success; errors $failed"
} finally {
    $writer.Dispose()
    if ($null -ne $app) {
        $app.Quit()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
    }
}
