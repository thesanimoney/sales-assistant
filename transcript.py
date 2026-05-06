from schemas import TranscriptEntry


def format_transcript(transcript: list[TranscriptEntry]) -> str:
    return "\n".join(f"{entry.speaker}: {entry.text}" for entry in transcript)
