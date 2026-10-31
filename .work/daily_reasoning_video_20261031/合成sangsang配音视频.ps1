[CmdletBinding()]
param(
    [string]$OutputPath = 'E:\XcodeProject_sang\短视频\第001期_只有才\第001讲_sangsang_配音成片.mp4',
    [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'
$ffmpeg = 'E:\JianyingPro\11.6.0.14552\ffmpeg.exe'
$assetDir = 'E:\XcodeProject_sang\短视频\第001期_只有才'
$images = @('01_先做一道题.png', '02_揭晓答案.png', '03_记住方法.png', '04_换题练一练.png') | ForEach-Object { Join-Path $assetDir $_ }
$audio = 1..4 | ForEach-Object { Join-Path $assetDir ('sangsang_第001讲_{0:00}.mp3' -f $_) }
$required = @($ffmpeg) + @($images) + @($audio)
$missing = @($required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($missing.Count) {
    throw ('缺少所需文件，未进行合成：' + [Environment]::NewLine + ($missing -join [Environment]::NewLine))
}
if (-not $CheckOnly -and (Test-Path -LiteralPath $OutputPath)) {
    throw "输出文件已存在，未覆盖：$OutputPath"
}

# 解码到空输出并读取最后一个时间戳，避免仅按 MP3 头部估计时长。
$durations = @()
for ($i = 0; $i -lt 4; $i++) {
    $progress = @(& $ffmpeg -hide_banner -loglevel error -i $audio[$i] -map '0:a:0' -f null - -progress 'pipe:1')
    if ($LASTEXITCODE -ne 0) { throw "无法读取配音：$($audio[$i])" }
    $lastTime = @($progress | Where-Object { $_ -match '^out_time_us=\d+$' } | Select-Object -Last 1)
    if (-not $lastTime.Count) { throw "无法确定配音时长：$($audio[$i])" }
    $seconds = [double]($lastTime[0] -replace '^out_time_us=', '') / 1000000.0
    if ($seconds -le 0) { throw "配音时长无效：$($audio[$i])" }
    $gap = if ($i -eq 0) { 3.0 } else { 0.4 }
    # 按完整视频帧向上取整，保证尾部停顿不会被截断。
    $duration = [Math]::Ceiling(($seconds + $gap) * 30.0) / 30.0
    $durations += $duration
    Write-Host ('第{0}段：音频 {1:F2} 秒，画面 {2:F2} 秒（含停顿 {3:F1} 秒）' -f ($i + 1), $seconds, $duration, $gap)
}
if ($CheckOnly) { Write-Host '检查完成，未合成。'; exit 0 }

$argsList = @('-hide_banner', '-n')
for ($i = 0; $i -lt 4; $i++) {
    $argsList += @('-loop', '1', '-framerate', '30', '-i', $images[$i], '-i', $audio[$i])
}
$filters = @()
for ($i = 0; $i -lt 4; $i++) {
    $v = $i * 2
    $a = $v + 1
    $d = $durations[$i].ToString('0.000000', [System.Globalization.CultureInfo]::InvariantCulture)
    $filters += "[$($v):v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p,trim=duration=$d,setpts=PTS-STARTPTS[v$i]"
    $filters += "[$($a):a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad,atrim=duration=$d,asetpts=PTS-STARTPTS[a$i]"
}
$filters += '[v0][a0][v1][a1][v2][a2][v3][a3]concat=n=4:v=1:a=1[vout][aout]'
$argsList += @('-filter_complex', ($filters -join ';'), '-map', '[vout]', '-map', '[aout]', '-c:v', 'h264_mf', '-b:v', '5000k', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', $OutputPath)
& $ffmpeg @argsList
if ($LASTEXITCODE -ne 0) { throw "合成失败（退出码 $LASTEXITCODE）。请检查输出文件是否完整：$OutputPath" }
Write-Host "合成完成：$OutputPath"
