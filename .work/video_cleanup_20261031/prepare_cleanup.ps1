$ErrorActionPreference='Stop'
$videoRoot=(Resolve-Path -LiteralPath 'E:\XcodeProject_sang\短视频').Path.TrimEnd('\')
$auditDir='E:\XcodeProject_sang\.work\video_cleanup_20261031'
$null=New-Item -ItemType Directory -Path $auditDir -Force
$candidates=@{}
function Add-Candidate([string]$path,[string]$category,[string]$reason) {
    $file=Get-Item -LiteralPath $path
    $absolute=[IO.Path]::GetFullPath($file.FullName)
    if (-not $absolute.StartsWith($videoRoot+'\',[StringComparison]::OrdinalIgnoreCase)) {throw "清理目标越界: $absolute"}
    if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint)) {throw "不是普通文件: $absolute"}
    $parent=$file.Directory
    while ($parent.FullName.Length -ge $videoRoot.Length) {
        if ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) {throw "父目录是链接: $absolute"}
        if ($parent.FullName -eq $videoRoot) {break}
        $parent=$parent.Parent
    }
    $candidates[$absolute.ToLowerInvariant()]=[pscustomobject]@{
        Path=$absolute; RelativePath=$absolute.Substring($videoRoot.Length+1)
        Category=$category; Reason=$reason; Bytes=$file.Length
        SHA256=(Get-FileHash -LiteralPath $absolute -Algorithm SHA256).Hash
    }
}
$ep1=Join-Path $videoRoot '第001期_只有才'
$ep2=Join-Path $videoRoot '第002期_去异求同'
Add-Candidate (Join-Path $ep1 '题卡总览.png') '可重建预览PNG' '题卡检查总览，不是正片输入'
Add-Candidate (Join-Path $ep2 '题卡总览.png') '可重建预览PNG' '题卡检查总览，不是正片输入'
$versions=@(
    @{Name='改进版_逐步演示'; Contact='动态关键帧总览.png'},
    @{Name='优化版_原题常驻'; Contact='原题常驻关键帧总览.png'},
    @{Name='优化版_去右上角期数'; Contact=$null}
)
foreach ($version in $versions) {
    $dir=Join-Path $ep2 $version.Name
    foreach ($file in (Get-ChildItem -LiteralPath $dir -File | Where-Object {$_.Name -match '^关键帧_\d{2}\.png$'})) {
        Add-Candidate $file.FullName '可重建预览PNG' '渲染源输出的关键帧，源码不读取'
    }
    foreach ($file in (Get-ChildItem -LiteralPath (Join-Path $dir '成片抽帧') -File | Where-Object {$_.Extension -eq '.png'})) {
        Add-Candidate $file.FullName '可重建预览PNG' '可从保留的MP4重新抽取'
    }
    Add-Candidate (Join-Path $dir '成片抽帧总览.png') '可重建预览PNG' '检查用拼图，完整视频及验证记录保留'
    if ($version.Contact) {Add-Candidate (Join-Path $dir $version.Contact) '可重建预览PNG' '历史版本关键帧总览，可由源重建'}
}
foreach ($name in @('音色克隆_讲题试听_01.mp3','sangsang_讲题试听.mp3','sangsang_首段_0.92倍试听.m4a','sangsang_首段_原速试听.m4a')) {
    Add-Candidate (Join-Path $ep1 $name) '废弃试听' '未用于正式有声视频，正式标准版和口音版原始音源保留'
}
Add-Candidate (Join-Path $ep1 '第001期_只有才_60秒_无声预览.mp4') '旧无声测试' '正式有声成片已保留，可由题卡重建；旧无声测试草稿可能缺媒体'
foreach ($name in @('01_先做一道题_15秒.mp4','02_揭晓答案_15秒.mp4','03_记住方法_16秒.mp4','04_换题练一练_14秒.mp4')) {
    Add-Candidate (Join-Path (Join-Path $ep1 '定时视频片段') $name) '旧无声测试' '初期固定时长试排片段，正式成片及题卡保留'
}
$sourceAudio=@{
    '002_01_原始配音.mp3'=Join-Path $ep2 '002_01_原始配音.mp3'
    '002_04_原始配音.mp3'=Join-Path $ep2 '002_04_原始配音.mp3'
    '002_v2_02_原始配音.mp3'=Join-Path (Join-Path $ep2 '改进版_逐步演示') '002_v2_02_原始配音.mp3'
    '002_v2_03_原始配音.mp3'=Join-Path (Join-Path $ep2 '改进版_逐步演示') '002_v2_03_原始配音.mp3'
}
foreach ($name in $sourceAudio.Keys) {
    $sourceHash=(Get-FileHash -LiteralPath $sourceAudio[$name] -Algorithm SHA256).Hash
    $latestCopy=Join-Path (Join-Path (Join-Path $ep2 '优化版_去右上角期数') '原始配音') $name
    if ((Get-FileHash -LiteralPath $latestCopy -Algorithm SHA256).Hash -ne $sourceHash) {throw "最终备份不一致: $name"}
    foreach ($version in @('改进版_逐步演示','优化版_原题常驻')) {
        $copy=Join-Path (Join-Path (Join-Path $ep2 $version) '原始配音') $name
        if ((Get-FileHash -LiteralPath $copy -Algorithm SHA256).Hash -ne $sourceHash) {throw "副本哈希不一致: $copy"}
        Add-Candidate $copy '重复配音备份' '与保留的默认音源及最新版本备份SHA-256相同，默认渲染路径不变'
    }
}
$selected=@($candidates.Values | Sort-Object Path)
if ($selected.Count -ne 104) {throw "候选数与审核不符: $($selected.Count)"}
$preserved=@(Get-ChildItem -LiteralPath $videoRoot -Recurse -File | Where-Object {-not $candidates.ContainsKey($_.FullName.ToLowerInvariant())} | ForEach-Object {
    [pscustomobject]@{Path=$_.FullName; Bytes=$_.Length; SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}
})
$manifest=[pscustomobject]@{
    Root=$videoRoot; Authorization='用户明确要求删除没用的本地生成素材'; PreparedAt=(Get-Date -Format o)
    Candidates=$selected; PreservedBaseline=$preserved
    DeleteCount=$selected.Count; DeleteBytes=($selected | Measure-Object Bytes -Sum).Sum
    KeptTemplatePreview=Join-Path (Join-Path $ep2 '优化版_去右上角期数') '无角标关键帧总览.png'
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $auditDir 'cleanup_manifest.json') -Encoding UTF8
$selected | Export-Csv -LiteralPath (Join-Path $auditDir 'cleanup_manifest.csv') -NoTypeInformation -Encoding UTF8
$selected | Group-Object Category | ForEach-Object {[pscustomobject]@{Category=$_.Name; Count=$_.Count; MiB=[math]::Round(($_.Group | Measure-Object Bytes -Sum).Sum/1MB,2)}} | ConvertTo-Json -Compress
Write-Output "待删 $($selected.Count) 文件，$([math]::Round($manifest.DeleteBytes/1MB,2)) MiB；保留 $($preserved.Count) 文件，清单已保存，尚未删除。"
