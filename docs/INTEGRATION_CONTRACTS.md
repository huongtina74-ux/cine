# Integration contracts

## Reasoning bridge
Input on stdin:

```json
{"stage":"director","prompt":"...","schema":{},"context":{}}
```

Output: one JSON object matching the supplied schema.

## Local TTS bridge
Text arrives on stdin. The configured command template can contain:

```text
{output} {language} {voice}
```

It must create the requested audio file.

## Local visual QC bridge
Input on stdin:

```json
{"media_path":"/abs/path/video.mp4","contract":{}}
```

Expected output:

```json
{
  "passed": true,
  "identity_score": 0.95,
  "continuity_score": 0.93,
  "performance_score": 0.88,
  "camera_score": 0.91,
  "findings": []
}
```

## OpenChatCut bridge
Receives CineFactory `TimelineSpec` JSON on stdin and may return a JSON result. This keeps the editor replaceable and avoids a second project database inside Factory Core.
