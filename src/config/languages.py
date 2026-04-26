SUPPORTED_LANGUAGES = {
    "english": "English",
    "french": "French",
    "hindi": "Hindi",
    "spanish": "Spanish",
    "german": "German",
    "telugu": "Telugu",
}


def normalize_language(language: str | None) -> str | None:
    if not language:
        return None

    normalized = language.strip().lower()
    if not normalized or normalized == "english":
        return None

    if normalized not in SUPPORTED_LANGUAGES:
        supported = ", ".join(SUPPORTED_LANGUAGES.values())
        raise ValueError(
            f"Translation for '{language}' is not supported yet. Supported languages: {supported}."
        )

    return normalized


def language_options() -> list[str]:
    return list(SUPPORTED_LANGUAGES.values())


def language_display_name(language_code: str | None) -> str:
    if not language_code:
        return "English"

    return SUPPORTED_LANGUAGES.get(language_code, language_code.title())
