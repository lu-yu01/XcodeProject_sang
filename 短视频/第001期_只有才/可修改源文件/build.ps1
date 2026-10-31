param([string]$OutputDir)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
if (-not $OutputDir) {
    $OutputDir = if ((Split-Path $PSScriptRoot -Leaf) -eq '可修改源文件') {
        Split-Path $PSScriptRoot -Parent
    } else {
        Join-Path $PSScriptRoot '..\..\短视频\第001期_只有才'
    }
}
$OutputDir = [IO.Path]::GetFullPath($OutputDir)
[IO.Directory]::CreateDirectory($OutputDir) | Out-Null
$script:Lesson = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'lesson.json') -Raw -Encoding utf8 | ConvertFrom-Json
$script:Metrics = [Collections.Generic.List[object]]::new()
$script:BG = '#101B2D'; $script:Panel = '#1A2A40'; $script:White = '#F3F6FA'
$script:Muted = '#AAB9CC'; $script:Mint = '#7DE3C0'; $script:Gold = '#F7CC79'
$script:FontName = 'Microsoft YaHei'

function Color([string]$Hex) { [Drawing.ColorTranslator]::FromHtml($Hex) }
function Box([int]$X,[int]$Y,[int]$W,[int]$H,[string]$Fill) {
    $b = [Drawing.SolidBrush]::new((Color $Fill))
    $script:G.FillRectangle($b,$X,$Y,$W,$H); $b.Dispose()
}
function Rule([int]$X,[int]$Y,[int]$W,[string]$Fill) { Box $X $Y $W 3 $Fill }
function Text([string]$Value,[int]$X,[int]$Y,[int]$Size,[string]$Fill=$script:White,[switch]$Bold,[int]$MaxW=840) {
    $style = if ($Bold) { [Drawing.FontStyle]::Bold } else { [Drawing.FontStyle]::Regular }
    $f = [Drawing.Font]::new($script:FontName,[single]$Size,$style,[Drawing.GraphicsUnit]::Pixel)
    $brush = [Drawing.SolidBrush]::new((Color $Fill))
    $fmt = [Drawing.StringFormat]::GenericTypographic.Clone()
    $fmt.FormatFlags = $fmt.FormatFlags -bor [Drawing.StringFormatFlags]::MeasureTrailingSpaces
    $measure = $script:G.MeasureString($Value,$f,10000,$fmt)
    if ($measure.Width -gt $MaxW) { throw "Text exceeds width: $Value ($($measure.Width) > $MaxW)" }
    $script:Metrics.Add([pscustomobject]@{scene=$script:Scene;text=$Value;x=$X;y=$Y;width=[math]::Round($measure.Width,1);height=[math]::Round($measure.Height,1);font_size=$Size})
    $script:G.DrawString($Value,$f,$brush,[single]$X,[single]$Y,$fmt)
    $fmt.Dispose(); $brush.Dispose(); $f.Dispose()
}
function Arrow([int]$X1,[int]$Y,[int]$X2,[string]$Fill=$script:Mint) {
    $p=[Drawing.Pen]::new((Color $Fill),8)
    $script:G.DrawLine($p,$X1,$Y,$X2,$Y)
    $script:G.DrawLine($p,$X2-22,$Y-19,$X2,$Y)
    $script:G.DrawLine($p,$X2-22,$Y+19,$X2,$Y)
    $p.Dispose()
}
function BeginCard([string]$Step,[int]$Progress) {
    $script:Scene=$Step
    $script:Bmp=[Drawing.Bitmap]::new(1080,1920)
    $script:G=[Drawing.Graphics]::FromImage($script:Bmp)
    $script:G.SmoothingMode=[Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $script:G.TextRenderingHint=[Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $script:G.Clear((Color $script:BG))
    # Right margin and lower area remain quiet for video-app controls and captions.
    Box 84 118 42 7 $script:Mint
    Text $script:Lesson.series 84 163 34 $script:Muted
    Text ('第'+$script:Lesson.episode+'期') 745 165 30 $script:Mint -MaxW 180
    Rule 84 235 836 '#304157'
    if($Progress -gt 0) { Box 84 235 ($Progress*209) 4 $script:Mint }
    Text $Step 84 270 28 $script:Gold
    Text $script:Lesson.source 84 1480 28 $script:Muted
    Text '每天一道题，讲透一个方法。' 84 1530 28 $script:Muted
}
function SaveCard([string]$File) {
    $path=Join-Path $OutputDir $File
    $script:Bmp.Save($path,[Drawing.Imaging.ImageFormat]::Png)
    $script:G.Dispose(); $script:Bmp.Dispose()
}
function Choices([int]$Y,[string]$A='能',[string]$B='不能确定') {
    Box 84 $Y 326 102 '#24364D'; Box 430 $Y 490 102 '#24364D'
    Text ('A  '+$A) 112 ($Y+22) 42 $script:White -MaxW 280
    Text ('B  '+$B) 458 ($Y+22) 42 $script:White -MaxW 430
}

BeginCard '本期主题' 0
Text '只有……' 84 355 105 $script:White -Bold
Text '才……' 84 500 105 $script:Mint -Bold
Box 84 735 836 440 $script:Panel
Text '这个箭头，' 126 793 67 $script:White -Bold -MaxW 750
Text '你写对了吗？' 126 895 67 $script:White -Bold -MaxW 750
Text '必要条件 · 翻译推理' 126 1083 34 $script:Muted -MaxW 750
Text '一道例题 + 一个方法 + 一道练习' 84 1283 35 $script:Gold
SaveCard '00_视频封面.png'

BeginCard '01 / 04    先做一道题' 1
Text '报名了，' 84 353 87 $script:White -Bold
Text '就一定能考？' 84 468 87 $script:Mint -Bold
Box 84 640 836 568 $script:Panel
Text '只有报名，' 126 694 63 $script:White -Bold -MaxW 750
Text '才能参加考试。' 126 788 63 $script:White -Bold -MaxW 750
Rule 126 909 752 '#3A4A60'
Text '小王报名了。' 126 963 46 $script:Muted -MaxW 750
Text '一定能参加考试吗？' 126 1046 52 $script:White -Bold -MaxW 750
Choices 1260
Text '先想 3 秒，再看解析。' 84 1415 31 $script:Gold
SaveCard $script:Lesson.cards[0].file

BeginCard '02 / 04    看清必要条件' 2
Text '答案是 B' 84 353 87 $script:White -Bold
Text '不能确定' 84 468 101 $script:Mint -Bold
Box 84 640 836 568 $script:Panel
Text '报名，只是必要条件。' 126 705 50 $script:White -Bold -MaxW 750
Text '题干没有说：' 126 840 40 $script:Muted -MaxW 750
Text '报名了，就一定能参加。' 126 914 49 $script:Gold -Bold -MaxW 750
Rule 126 1031 752 '#3A4A60'
Text '还可能有其他参加条件。' 126 1087 42 $script:White -MaxW 750
Text '满足必要条件，结果仍不确定。' 84 1307 40 $script:White -Bold
Text '判断能否推出，要以题干信息为准。' 84 1407 30 $script:Muted
SaveCard $script:Lesson.cards[1].file

BeginCard '03 / 04    记住翻译方法' 3
Text '只有 A，才 B' 84 353 81 $script:White -Bold
Text '翻译成：B 推 A' 84 478 75 $script:Mint -Bold
Box 84 640 836 568 $script:Panel
Text '对应本题' 126 689 31 $script:Muted -MaxW 750
Text '能参加' 126 778 59 $script:White -Bold -MaxW 260
Arrow 380 818 520
Text '已报名' 568 778 59 $script:Mint -Bold -MaxW 300
Rule 126 912 752 '#3A4A60'
Text '逆否也成立' 126 955 31 $script:Muted -MaxW 750
Text '没报名' 126 1043 53 $script:White -Bold -MaxW 260
Arrow 380 1081 520
Text '不能参加' 568 1043 50 $script:Mint -Bold -MaxW 310
Text '把“才”后面的内容，放在箭头前。' 84 1307 39 $script:White -Bold
Text '箭头表示“能推出”，别写反。' 84 1407 31 $script:Gold
SaveCard $script:Lesson.cards[2].file

BeginCard '04 / 04    换一道题试试' 4
Text '这次，' 84 353 87 $script:White -Bold
Text '你能判断吗？' 84 468 87 $script:Mint -Bold
Box 84 640 836 568 $script:Panel
Text '只有审核通过，' 126 694 59 $script:White -Bold -MaxW 750
Text '才能入职。' 126 785 59 $script:White -Bold -MaxW 750
Rule 126 906 752 '#3A4A60'
Text '小李没有入职。' 126 955 45 $script:Muted -MaxW 750
Text '能推出“审核没通过”吗？' 126 1045 47 $script:White -Bold -MaxW 750
Choices 1260
Text '评论区写下答案和理由。' 84 1415 32 $script:Gold
SaveCard $script:Lesson.cards[3].file

# Contact sheet: preview of the four content cards, not a video frame.
$contact=[Drawing.Bitmap]::new(1080,2050)
$cg=[Drawing.Graphics]::FromImage($contact)
$cg.Clear((Color '#E9EDF2'))
$cg.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
for($i=0;$i -lt 4;$i++){
    $img=[Drawing.Image]::FromFile((Join-Path $OutputDir $script:Lesson.cards[$i].file))
    $cg.DrawImage($img,(32+($i%2)*526),(90+[math]::Floor($i/2)*942),490,871)
    $img.Dispose()
}
$f=[Drawing.Font]::new($script:FontName,29,[Drawing.FontStyle]::Bold,[Drawing.GraphicsUnit]::Pixel)
$br=[Drawing.SolidBrush]::new((Color '#101B2D'))
$cg.DrawString('第001期 · 四张内容题卡预览',$f,$br,30,25)
$cg.DrawString('1080 × 1920 竖屏 PNG / 按 01—04 顺序导入',$f,$br,30,1940)
$cg.DrawString('配音后按实际录音调整每张停留时间。',$f,$br,30,1990)
$cg.Dispose();$f.Dispose();$br.Dispose()
$contact.Save((Join-Path $OutputDir '题卡总览.png'),[Drawing.Imaging.ImageFormat]::Png)
$contact.Dispose()

$lines=[Collections.Generic.List[string]]::new()
$lines.Add('第001期｜只有……才……｜逐页录音稿')
$lines.Add('')
$lines.Add('录音方法：每页单独录一段；只读下面的口播文字，不读页码和时间。保持自然语速。')
$lines.Add('时间为60秒参考编排，不是已完成的配音时长；可按实际录音延长或缩短。')
$start=0
foreach($card in $script:Lesson.cards){
    $end=$start+$card.seconds
    $lines.Add('')
    $lines.Add(('【{0}｜{1}—{2}秒】' -f $card.label,$start,$end))
    $lines.Add($card.voice)
    if($card.pause -gt 0){$lines.Add(('（此处留{0}秒思考时间，不用朗读。）' -f $card.pause))}
    $start=$end
}
[IO.File]::WriteAllLines((Join-Path $OutputDir '配音稿.txt'),$lines,[Text.UTF8Encoding]::new($true))

$guide=@'
第001期｜“题卡＋自己的配音”制作说明

素材内容
00_视频封面.png：只用作封面，不计入正片60秒。
01—04：四张正片题卡，均为1080×1920、9:16、PNG。
题卡总览.png：检查与预览用，不导入正片。
配音稿.txt：逐页录音文字，每页可单独录音。
可修改源文件：lesson.json保存配音文字；build.ps1保存题卡文字、颜色和排版。

剪辑顺序（界面名称以你的剪辑软件实际显示为准）
1. 新建9:16竖屏项目，按01、02、03、04导入四张图片。
2. 图片铺满画面并保持原比例。先设置参考时长15、15、16、14秒。
3. 用安静环境录制自己的声音，每张题卡一段，放在对应图片下方。
4. 按实际录音调整图片时长；第一页在读完“先停三秒”后留3秒。
5. 首版直接切换题卡即可；题卡上的箭头和重点已经画好。
6. 如添加自动字幕，校对“只有A，才B”“B推A”“报名”“审核”；字幕放在画面下方留白处，根据发布预览调整位置，避免盖住题干和平台文案。
7. 封面选00；导出建议为1080×1920、30帧/秒。试听整条视频，并检查实际发布预览中的右侧按钮和底部文字遮挡。

参考时间表
00:00—00:15  01_先做一道题.png，含末尾3秒思考。
00:15—00:30  02_揭晓答案.png。
00:30—00:46  03_记住方法.png。
00:46—01:00  04_换题练一练.png。
这是剪辑起点；录音后的实际时长优先，不要为了凑60秒强行加速。

内容核对
本期为原创基础教学示例，不标注为考试真题。
只有A，才B，即B→A；等价逆否为非A→非B。
例题：A=报名，B=能参加考试。报名不能推出一定能参加，答案B“不能确定”。
练习：A=审核通过，B=入职。没有入职，无法确定审核是否通过，答案B“不能确定”。
练习题卡保留问题，答案在这里供你核对。下一条视频开头可先解释练习答案，再讲“如果……那么……”。

发布文案草稿
标题：“只有……才……”的箭头，你写对了吗？｜判断推理第001讲
正文：每天一道题，讲透一个方法。这期讲必要条件：只有A，才B，翻译成B推A。最后一道练习，你选A还是B？
话题草稿：#判断推理 #行测 #逻辑判断 #每日一题
置顶评论草稿（看需要使用）：练习答案：B，不能确定。没入职，审核可能通过，也可能没通过。

每天复用的制作清单
确定一个知识点 → 核对题目与答案 → 替换四张题卡 → 每页录音 → 按声音调整时长 → 通看成片 → 设封面与发布文案。
当前交付是题卡与录音/剪辑素材；尚未录制人声、合成成片或发布。
'@
[IO.File]::WriteAllText((Join-Path $OutputDir '制作说明.txt'),$guide,[Text.UTF8Encoding]::new($true))
$src=Join-Path $OutputDir '可修改源文件'
[IO.Directory]::CreateDirectory($src) | Out-Null
if ([IO.Path]::GetFullPath($PSScriptRoot) -ne [IO.Path]::GetFullPath($src)) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'lesson.json') -Destination $src -Force
    Copy-Item -LiteralPath $PSCommandPath -Destination $src -Force
}
$script:Metrics | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $OutputDir '文字边界检查.json') -Encoding utf8
Write-Output "Created: $OutputDir"
Write-Output ('Total voice reference: '+$start+' seconds')
