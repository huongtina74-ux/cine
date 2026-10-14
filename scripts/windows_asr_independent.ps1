param(
    [Parameter(Mandatory=$true)][string]$InputWav,
    [Parameter(Mandatory=$true)][string]$OutputJson,
    [string]$Culture='en-US',
    [int]$TimeoutSeconds=8
)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$wav=[System.IO.Path]::GetFullPath($InputWav)
if(-not [System.IO.File]::Exists($wav)){throw 'INDEPENDENT_ASR_INPUT_MISSING'}
$available=@([System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers())
$recognizer=$available | Where-Object {$_.Culture.Name -eq $Culture} | Select-Object -First 1
if($null -eq $recognizer){throw 'INDEPENDENT_ASR_RECOGNIZER_NOT_INSTALLED'}
$engine=New-Object System.Speech.Recognition.SpeechRecognitionEngine -ArgumentList ([System.Globalization.CultureInfo]$Culture)
try {
    # DictationGrammar does NOT include expected transcript or word timestamps.
    $engine.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
    $engine.SetInputToWaveFile($wav)
    $result=$engine.Recognize([TimeSpan]::FromSeconds($TimeoutSeconds))
    $observed=@()
    if($null -ne $result){
        foreach($word in $result.Words){
            $observed+=@([pscustomobject]@{
                text=[string]$word.Text
                lexical_form=[string]$word.LexicalForm
                confidence=[double]$word.Confidence
            })
        }
    }
    $sha=Get-FileHash -Algorithm SHA256 -LiteralPath $wav
    $output=[ordered]@{
        source='WINDOWS_SYSTEM_SPEECH_RECOGNITION_DICTATION'
        recognizer=[string]$recognizer.Name
        culture=$Culture
        source_wav=$wav
        source_sha256=$sha.Hash.ToLowerInvariant()
        recognized=$null -ne $result
        transcript=if($null -ne $result){[string]$result.Text}else{''}
        confidence=if($null -ne $result){[double]$result.Confidence}else{0.0}
        words=@($observed)
        time_aligned_words_available=$false
        forced_phoneme_alignment_verified=$false
        transcript_supplied_to_recognizer=$false
    }
    $utf8=New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText(
        [System.IO.Path]::GetFullPath($OutputJson),
        ($output | ConvertTo-Json -Depth 8),$utf8
    )
    Write-Output ('ASR_DICTATION:'+($output.transcript)+'; confidence='+($output.confidence))
}
finally {
    $engine.Dispose()
}