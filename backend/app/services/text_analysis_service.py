import re


FILLER_WORDS = {
    "um",
    "uh",
    "like",
    "basically",
    "actually",
    "you know",
    "sort of",
    "kind of",
    "literally"
}


def count_filler_words(transcript: str) -> int:
    transcript_lower = transcript.lower()

    count = 0

    for filler in FILLER_WORDS:
        count += transcript_lower.count(filler)

    return count


def analyse_text(
    transcript: str,
    relevance_result: dict
) -> dict:
    """
    Analyse the transcript using linguistic
    features together with semantic relevance.

    Total text score = 100

    Length       : 20
    Structure    : 20
    Clarity      : 20
    Relevance    : 40
    """

    # ----------------------------
    # Basic statistics
    # ----------------------------

    words = re.findall(r"\b\w+\b", transcript)

    sentences = re.split(
        r"[.!?]+",
        transcript
    )

    sentences = [
        s.strip()
        for s in sentences
        if s.strip()
    ]

    word_count = len(words)

    sentence_count = len(sentences)

    filler_count = count_filler_words(
        transcript
    )

    # ----------------------------
    # Linguistic scores
    # ----------------------------

    # 80 words or more receives full marks.

    length_score = min(
        word_count / 80,
        1.0
    ) * 20

    # Four sentences receives full marks.

    structure_score = min(
        sentence_count / 4,
        1.0
    ) * 20

    # Deduct marks for filler words.

    clarity_score = max(
        0,
        20 - (filler_count * 3)
    )

    # ----------------------------
    # Semantic relevance
    # ----------------------------

    relevance_score = relevance_result[
        "relevance_score"
    ]

    semantic_similarity = relevance_result[
        "semantic_similarity"
    ]

    relevance_label = relevance_result[
        "relevance_label"
    ]

    # ----------------------------
    # Final text score
    # ----------------------------

    text_score = round(

        length_score

        + structure_score

        + clarity_score

        + relevance_score,

        2

    )

    return {

        "text_score": text_score,

        "word_count": word_count,

        "sentence_count": sentence_count,

        "filler_words": filler_count,

        "length_score": round(
            length_score,
            2
        ),

        "structure_score": round(
            structure_score,
            2
        ),

        "clarity_score": round(
            clarity_score,
            2
        ),

        "relevance_score": round(
            relevance_score,
            2
        ),

        "semantic_similarity": round(
            semantic_similarity,
            3
        ),

        "relevance_label": relevance_label

    }