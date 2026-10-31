param([int]$Index)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$wav = Join-Path $PSScriptRoot ('sample_{0:00}.wav' -f $Index)
$engine = [System.Speech.Recognition.SpeechRecognitionEngine]::new([System.Globalization.CultureInfo]::GetCultureInfo('zh-CN'))
$engine.LoadGrammar([System.Speech.Recognition.DictationGrammar]::new())
$engine.SetInputToWaveFile($wav)
$segments = @()
while ($null -ne ($result = $engine.Recognize())) {
    $segments += [pscustomobject]@{Start=$result.Audio.AudioPosition.TotalSeconds; Duration=$result.Audio.Duration.TotalSeconds; Confidence=$result.Confidence; Text=$result.Text}
}
$engine.Dispose()
$data = [pscustomobject]@{Index=$Index; Segments=$segments}
$data | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $PSScriptRoot ('recognition_{0:00}.json' -f $Index)) -Encoding UTF8
$data | ConvertTo-Json -Depth 4 -Compress
