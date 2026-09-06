from app.core.config import Settings


def test_settings_work_without_ai_or_stt_credentials(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("STT_API_KEY", raising=False)

    settings = Settings(_env_file=None)

    assert settings.gemini_api_key is None
    assert settings.stt_api_key is None
    assert settings.ai_enabled is False
    assert settings.stt_enabled is False


def test_cors_origin_list_parses_comma_separated_values():
    settings = Settings(_env_file=None, cors_origins="http://a.test, http://b.test")

    assert settings.cors_origin_list == ["http://a.test", "http://b.test"]
