$ErrorActionPreference='Stop'
$auditDir='E:\XcodeProject_sang\.work\video_cleanup_20261031'
$manifest=Get-Content -LiteralPath (Join-Path $auditDir 'cleanup_manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$expectedRoot=[IO.Path]::GetFullPath('E:\XcodeProject_sang\短视频').TrimEnd('\')
$actualRoot=(Resolve-Path -LiteralPath $manifest.Root).Path.TrimEnd('\')
if ($actualRoot -ne $expectedRoot -or @($manifest.Candidates).Count -ne 104) {throw '根目录或清单数量不符'}
if (Test-Path -LiteralPath (Join-Path $auditDir 'cleanup_result.json')) {throw '已有执行结果，停止重复清理'}
# Validate every absolute file and hash before deleting anything. No recursive removal.
foreach ($entry in $manifest.Candidates) {
    $file=Get-Item -LiteralPath $entry.Path
    $absolute=[IO.Path]::GetFullPath($file.FullName)
    if ($absolute -ne $entry.Path -or -not $absolute.StartsWith($expectedRoot+'\',[StringComparison]::OrdinalIgnoreCase)) {throw "越界目标: $absolute"}
    if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint)) {throw "目标类型不符: $absolute"}
    $parent=$file.Directory
    while ($parent.FullName.Length -ge $expectedRoot.Length) {
        if ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) {throw "父目录是链接: $absolute"}
        if ($parent.FullName -eq $expectedRoot) {break}
        $parent=$parent.Parent
    }
    if ($file.Length -ne $entry.Bytes -or (Get-FileHash -LiteralPath $absolute -Algorithm SHA256).Hash -ne $entry.SHA256) {throw "审核后文件改变: $absolute"}
}
foreach ($entry in $manifest.PreservedBaseline) {
    if (-not (Test-Path -LiteralPath $entry.Path -PathType Leaf)) {throw "保留文件缺失: $($entry.Path)"}
    if ((Get-FileHash -LiteralPath $entry.Path -Algorithm SHA256).Hash -ne $entry.SHA256) {throw "保留文件改变: $($entry.Path)"}
}
$deleted=[Collections.Generic.List[string]]::new()
try {
    foreach ($entry in $manifest.Candidates) {
        Remove-Item -LiteralPath $entry.Path -Force
        $deleted.Add($entry.Path)
    }
} finally {
    [pscustomobject]@{ExecutedAt=(Get-Date -Format o); DeletedFiles=$deleted.ToArray(); DeletedCount=$deleted.Count} |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $auditDir 'cleanup_execution.json') -Encoding UTF8
}
foreach ($entry in $manifest.Candidates) {if (Test-Path -LiteralPath $entry.Path) {throw "目标仍存在: $($entry.Path)"}}
foreach ($entry in $manifest.PreservedBaseline) {
    if (-not (Test-Path -LiteralPath $entry.Path -PathType Leaf) -or (Get-FileHash -LiteralPath $entry.Path -Algorithm SHA256).Hash -ne $entry.SHA256) {throw "保留文件核对失败: $($entry.Path)"}
}
$emptyDirs=[Collections.Generic.List[string]]::new()
foreach ($parentPath in @($manifest.Candidates | ForEach-Object {Split-Path -LiteralPath $_.Path} | Sort-Object -Unique)) {
    $absolute=[IO.Path]::GetFullPath($parentPath)
    if ($absolute.StartsWith($expectedRoot+'\',[StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $absolute -PathType Container)) {
        if (@(Get-ChildItem -LiteralPath $absolute -Force).Count -eq 0) {
            Remove-Item -LiteralPath $absolute
            $emptyDirs.Add($absolute)
        }
    }
}
$result=[pscustomobject]@{
    CompletedAt=(Get-Date -Format o); Root=$expectedRoot; DeletedCount=$deleted.Count
    DeletedBytes=$manifest.DeleteBytes; DeletedMiB=[math]::Round($manifest.DeleteBytes/1MB,2)
    PreservedCount=@($manifest.PreservedBaseline).Count; PreservedHashesUnchanged=$true
    DeletedFiles=$deleted.ToArray(); RemovedEmptyDirectories=$emptyDirs.ToArray()
    Note='正式视频、源题卡、实际原始音源、源码和最新模板参考图保留；旧无声测试草稿可能缺媒体。'
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $auditDir 'cleanup_result.json') -Encoding UTF8
$result | Select-Object DeletedCount,DeletedMiB,PreservedCount,PreservedHashesUnchanged | ConvertTo-Json -Compress
