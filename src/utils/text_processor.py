"""
Text Processor & Expressive Prosody Optimizer for Voxel.
Enhances text before speech synthesis so neural voices deliver rich emotion,
natural breathing pauses, clear questions, and engaging presentations.
Also provides sentence/clause chunking for instant sub-second playback.
"""
import re
from typing import List


def prepare_expressive_text(text: str, emotion_mode: str = "expressive") -> str:
    """
    Cleans and optimizes raw document text, presentation slides, or selected text
    for maximum vocal expressiveness, clarity, and natural pacing.
    """
    if not text:
        return ""

    t = text.strip()

    # 1. Expand URLs into spoken friendly domain names
    t = re.sub(
        r"https?://(?:www\.)?([a-zA-Z0-9.-]+)(?:/[^\s]*)?",
        r"website \1",
        t
    )

    # 2. Normalize bullet points and list dashes into natural breathing pauses
    t = re.sub(r"^\s*[\u2022\u2023\u25E6\u2043\u2219\*\-]\s*", "• ", t, flags=re.MULTILINE)
    t = re.sub(r"•\s*", " , ", t)

    # 3. Clean consecutive ellipsis and dashes into natural breath pauses
    t = re.sub(r"\.{3,}", " ... ", t)
    t = re.sub(r"\s*—\s*", " , ", t)
    t = re.sub(r"\s*--\s*", " , ", t)

    # 4. Clean email addresses into readable format
    t = re.sub(r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", r"\1 at \2", t)

    # 5. Fix multiple exclamation points or question marks into single expressive marks
    t = re.sub(r"!{2,}", "!", t)
    t = re.sub(r"\?{2,}", "?", t)

    # 6. Normalize whitespace
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{2,}", "\n\n", t)

    return t.strip()


def split_into_speech_chunks(text: str, min_chars: int = 40, max_chars: int = 180) -> List[str]:
    """
    Splits text into natural sentence batches for streaming playback.
    The first chunk is kept short (~50-100 chars) so audio begins playing
    almost instantly, while subsequent chunks batch 2-3 sentences.
    """
    cleaned = prepare_expressive_text(text)
    if not cleaned:
        return []

    # Regex to split on sentence terminators (. ! ? \n\n) while keeping delimiters
    raw_sentences = re.split(r"(?<=[.!?\n])\s+", cleaned)
    raw_sentences = [s.strip() for s in raw_sentences if s.strip()]

    if not raw_sentences:
        return [cleaned]

    chunks: List[str] = []
    current_chunk = ""

    # Always keep chunk 0 short for near-instant Time-To-First-Audio (TTFA)
    is_first_chunk = True
    target_max = 90  # First sentence starts in < 300ms

    for sentence in raw_sentences:
        if not current_chunk:
            current_chunk = sentence
        elif len(current_chunk) + len(sentence) + 1 <= target_max:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
            if is_first_chunk:
                is_first_chunk = False
                target_max = max_chars  # Subsequent chunks can be larger

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
