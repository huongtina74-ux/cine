from cinefactory.studio.audio_conference import (
    AudioConferenceRequest,
    AudioObjective,
    AudioProductionConference,
    default_audio_engine_candidates,
)


def _conference(*, tts_mode="none", has_command=False):
    return AudioProductionConference(
        default_audio_engine_candidates(
            tts_mode=tts_mode,
            has_tts_command=has_command,
            ffmpeg_executable=True,
        )
    )


def test_command_tts_wins_dialogue_after_all_hard_gates():
    request = AudioConferenceRequest(
        job_id="DLG_0001",
        scene_id="S1",
        objective=AudioObjective.CHARACTER_DIALOGUE,
        max_vram_gb=12.0,
        min_quality=0.70,
        require_commercial_safe=True,
    )
    decision = _conference(
        tts_mode="command",
        has_command=True,
    ).deliberate(request)

    assert decision.blocked is False
    assert decision.primary_engine_id == "tts.command"
    command = next(
        item for item in decision.assessments
        if item.engine_id == "tts.command"
    )
    assert "COMMERCIAL_LICENSE_USER_MANAGED" in command.warnings


def test_auk_pytorch_is_blocked_on_12gb_and_commercial_gate():
    request = AudioConferenceRequest(
        job_id="DLG_0002",
        objective=AudioObjective.EXPRESSIVE_DIALOGUE,
        max_vram_gb=12.0,
        min_quality=0.70,
        require_commercial_safe=True,
    )
    decision = _conference().deliberate(request)
    auk = next(
        item for item in decision.assessments
        if item.engine_id == "auk.pytorch.base"
    )
    assert auk.eligible is False
    assert "COMMERCIAL_LICENSE_RESTRICTED" in auk.blockers
    assert "VRAM_BUDGET_EXCEEDED" in auk.blockers


def test_auk_audio_cpp_stays_blocked_until_vram_is_verified():
    request = AudioConferenceRequest(
        job_id="DLG_0003",
        objective=AudioObjective.CHARACTER_DIALOGUE,
        max_vram_gb=12.0,
        min_quality=0.70,
        require_commercial_safe=True,
        require_vram_verified=True,
    )
    decision = _conference().deliberate(request)
    gguf = next(
        item for item in decision.assessments
        if item.engine_id == "auk.audio_cpp.flash"
    )

    assert gguf.eligible is False
    assert "COMMERCIAL_LICENSE_RESTRICTED" in gguf.blockers
    assert "VRAM_UNVERIFIED" in gguf.blockers


def test_voice_clone_never_falls_back_to_plain_tts():
    request = AudioConferenceRequest(
        job_id="DLG_CLONE",
        objective=AudioObjective.VOICE_CLONE,
        voice_reference="voices/hero.wav",
        max_vram_gb=12.0,
        min_quality=0.70,
        require_commercial_safe=True,
    )
    decision = _conference(
        tts_mode="command",
        has_command=True,
    ).deliberate(request)

    assert decision.blocked is True
    assert decision.primary_engine_id is None
    plain_tts = next(
        item for item in decision.assessments
        if item.engine_id == "tts.command"
    )
    assert "OBJECTIVE_UNSUPPORTED" in plain_tts.blockers


def test_voice_clone_requires_reference_even_for_capable_engine():
    request = AudioConferenceRequest(
        job_id="DLG_CLONE_NO_REF",
        objective=AudioObjective.VOICE_CLONE,
        max_vram_gb=24.0,
        min_quality=0.70,
        require_commercial_safe=False,
    )
    decision = _conference().deliberate(request)
    capable = [
        item for item in decision.assessments
        if item.engine_id.startswith("auk.")
    ]

    assert capable
    assert all(
        "VOICE_REFERENCE_REQUIRED" in item.blockers
        for item in capable
    )


def test_ffmpeg_is_selected_for_mix_and_speech_enhancement():
    conference = _conference()
    for objective in (
        AudioObjective.MIX_MASTER,
        AudioObjective.SPEECH_ENHANCEMENT,
    ):
        decision = conference.deliberate(
            AudioConferenceRequest(
                job_id=f"JOB_{objective.value}",
                objective=objective,
                min_quality=0.70,
                require_commercial_safe=True,
            )
        )
        assert decision.blocked is False
        assert decision.primary_engine_id == "ffmpeg.audio"


def test_source_separation_fails_closed_without_safe_qualified_engine():
    decision = _conference().deliberate(
        AudioConferenceRequest(
            job_id="SEP_1",
            objective=AudioObjective.SOURCE_SEPARATION,
            max_vram_gb=12.0,
            min_quality=0.70,
            require_commercial_safe=True,
        )
    )

    assert decision.blocked is True
    assert decision.primary_engine_id is None
    assert decision.reasons == ["NO_AUDIO_ENGINE_PASSED_ALL_GATES"]


def test_espeak_is_rejected_by_production_quality_gate():
    decision = _conference(tts_mode="espeak").deliberate(
        AudioConferenceRequest(
            job_id="DLG_LOW_QUALITY",
            objective=AudioObjective.NARRATION,
            min_quality=0.70,
            require_commercial_safe=True,
        )
    )
    espeak = next(
        item for item in decision.assessments
        if item.engine_id == "tts.espeak"
    )
    assert "QUALITY_GATE_FAILED" in espeak.blockers
    assert decision.blocked is True


def test_cosyvoice3_beats_plain_command_tts_when_qualified():
    conference = AudioProductionConference(
        default_audio_engine_candidates(
            tts_mode="command",
            has_tts_command=True,
            cosyvoice_executable=True,
            cosyvoice_qualified=True,
            cosyvoice_vram_gb=6.0,
            cosyvoice_vram_verified=True,
        )
    )
    decision = conference.deliberate(
        AudioConferenceRequest(
            job_id="DLG_COSY",
            objective=AudioObjective.CHARACTER_DIALOGUE,
            max_vram_gb=12.0,
            require_commercial_safe=True,
        )
    )
    assert decision.blocked is False
    assert decision.primary_engine_id == "cosyvoice3.local"


def test_cosyvoice3_supports_voice_clone_only_with_reference():
    conference = AudioProductionConference(
        default_audio_engine_candidates(
            cosyvoice_executable=True,
            cosyvoice_qualified=True,
            cosyvoice_vram_gb=6.0,
            cosyvoice_vram_verified=True,
        )
    )
    blocked = conference.deliberate(
        AudioConferenceRequest(
            job_id="CLONE_NO_REF",
            objective=AudioObjective.VOICE_CLONE,
            max_vram_gb=12.0,
        )
    )
    assert blocked.blocked is True
    ready = conference.deliberate(
        AudioConferenceRequest(
            job_id="CLONE_REF",
            objective=AudioObjective.VOICE_CLONE,
            voice_reference="voices/hero.wav",
            max_vram_gb=12.0,
        )
    )
    assert ready.blocked is False
    assert ready.primary_engine_id == "cosyvoice3.local"
