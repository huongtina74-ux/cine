param(
    [Parameter(Mandatory=$true)][string]$RequestPath
)
$ErrorActionPreference = 'Stop'
try {
    Add-Type -AssemblyName System.Speech
    $request = Get-Content -LiteralPath $RequestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace($request.text) -or $request.text.Length -gt 900) { throw 'INVALID_TTS_TEXT' }
    $wav = [System.IO.Path]::GetFullPath([string]$request.audio_path)
    $eventsPath = [System.IO.Path]::GetFullPath([string]$request.events_path)
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($wav)) | Out-Null
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($eventsPath)) | Out-Null
    $tts = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $events = New-Object 'System.Collections.Generic.List[object]'
    $words = New-Object 'System.Collections.Generic.List[object]'
    try {
        $voice = [string]$request.voice
        $available = @($tts.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name })
        if ($voice -notin $available) { throw "TTS_VOICE_NOT_INSTALLED:$voice" }
        $tts.SelectVoice($voice)
        $tts.Rate = 0
        $tts.Volume = 100
        $tts.add_VisemeReached({
            param($sender,$event)
            $events.Add([pscustomobject]@{
                viseme = [int]$event.Viseme
                time_seconds = [double]$event.AudioPosition.TotalSeconds
                duration_seconds = [double]$event.Duration.TotalSeconds
                next_viseme = [int]$event.NextViseme
                emphasis = [string]$event.Emphasis
            })
        })
        $tts.add_SpeakProgress({
            param($sender,$event)
            $words.Add([pscustomobject]@{
                text = [string]$event.Text
                time_seconds = [double]$event.AudioPosition.TotalSeconds
                character_position = [int]$event.CharacterPosition
                character_count = [int]$event.CharacterCount
            })
        })
        $tts.SetOutputToWaveFile($wav)
        $tts.Speak([string]$request.text)
        $tts.SetOutputToNull()
        if (!(Test-Path -LiteralPath $wav) -or (Get-Item -LiteralPath $wav).Length -le 44) {
            throw "TTS_WAV_EMPTY"
        }
        $result = [ordered]@{
            engine = "WINDOWS_SYSTEM_SPEECH_SAPI"
            voice = $voice
            text = [string]$request.text
            event_source = "SYNTHESIZER_VISEME_REACHED"
            wav_path = $wav
            wav_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $wav).Hash.ToLowerInvariant()
            viseme_events = @($events.ToArray())
            event_count = [int]$events.Count
            word_events = @($words.ToArray())
            word_event_count = [int]$words.Count
            word_source = "SYNTHESIZER_SPEAK_PROGRESS"
        }
        if ($events.Count -eq 0) { throw "SAPI_DID_NOT_EMIT_VISEMES" }
        $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $eventsPath -Encoding UTF8
        Write-Output ("SAPI_REAL_VISEMES=" + $events.Count)
    } finally { $tts.Dispose() }
} catch {
    Write-Error ("SAPI_SYNTHESIS_FAILED: " + $_.Exception.Message)
    exit 1
}
