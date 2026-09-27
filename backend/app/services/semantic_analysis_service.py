import re

from sentence_transformers import SentenceTransformer, util

try:
    model = SentenceTransformer(
        "all-MiniLM-L6-v2",
        local_files_only=True
    )
except Exception:
    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

def split_into_sentences(
    transcript: str
) -> list[str]:
    """
    Split the transcript using sentence-ending
    punctuation produced by Whisper.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        transcript.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def analyse_relevance(
    reference_text: str,
    transcript: str,
    expected_topics: list[str] | None = None
) -> dict:
    """
    Evaluate answer relevance using two components:

    1. Semantic similarity between the expected-answer
       reference and candidate response.
    2. Coverage of expected interview topics.

    Final relevance:
        60% topic coverage
        40% semantic similarity
    """

    if expected_topics is None:

        expected_topics = []

    if not transcript.strip():

        return {
            "semantic_similarity": 0.0,
            "semantic_score": 0.0,
            "topic_coverage": 0.0,
            "topic_score": 0.0,
            "matched_topics": [],
            "missing_topics": expected_topics,
            "relevance_score": 0.0,
            "relevance_label": "Not Relevant"
        }

    # -------------------------------------------------
    # Split transcript
    # -------------------------------------------------

    sentences = split_into_sentences(
        transcript
    )

    if not sentences:

        sentences = [transcript.strip()]

    # -------------------------------------------------
    # Semantic similarity
    # -------------------------------------------------

    reference_embedding = model.encode(
        reference_text,
        convert_to_tensor=True
    )

    transcript_embedding = model.encode(
        transcript,
        convert_to_tensor=True
    )

    similarity = util.cos_sim(
        reference_embedding,
        transcript_embedding
    ).item()

    similarity = max(
        0.0,
        min(1.0, similarity)
    )

    minimum_similarity = 0.15
    strong_similarity = 0.60

    normalised_similarity = (
        similarity - minimum_similarity
    ) / (
        strong_similarity - minimum_similarity
    )

    normalised_similarity = max(
        0.0,
        min(1.0, normalised_similarity)
    )

    semantic_score = normalised_similarity * 40

    # -------------------------------------------------
    # Expected-topic coverage
    # -------------------------------------------------

    matched_topics = []
    missing_topics = []

    if expected_topics:

        sentence_embeddings = model.encode(
            sentences,
            convert_to_tensor=True
        )

        topic_embeddings = model.encode(
            expected_topics,
            convert_to_tensor=True
        )

        topic_sentence_scores = util.cos_sim(
            topic_embeddings,
            sentence_embeddings
        )

        # A topic is considered present when at least
        # one transcript sentence reaches this value.
        topic_match_threshold = 0.30

        for index, topic in enumerate(
            expected_topics
        ):

            best_similarity = (
                topic_sentence_scores[index]
                .max()
                .item()
            )

            if best_similarity >= topic_match_threshold:

                matched_topics.append(topic)

            else:

                missing_topics.append(topic)

        topic_coverage = (
            len(matched_topics)
            / len(expected_topics)
        )

        topic_score = topic_coverage * 40

        # Hybrid scoring:
        # Combine the two 0–40 component scores.
        # Topic coverage receives greater weight because
        # it provides a more interpretable indication of
        # whether expected answer content was addressed.
        relevance_score = (
            topic_score * 0.60
            +
            semantic_score * 0.40
        )

    else:

        # Custom questions have no predefined rubric.
        # Use semantic scoring only.
        topic_coverage = 0.0
        topic_score = 0.0
        relevance_score = semantic_score

    relevance_score = round(
        max(
            0.0,
            min(40.0, relevance_score)
        ),
        2
    )

    # -------------------------------------------------
    # Human-readable label
    # -------------------------------------------------

    if relevance_score >= 30:

        label = "Highly Relevant"

    elif relevance_score >= 20:

        label = "Moderately Relevant"

    elif relevance_score >= 10:

        label = "Partially Relevant"

    else:

        label = "Not Relevant"

    return {

        "semantic_similarity": round(
            similarity,
            3
        ),

        "semantic_score": round(
            semantic_score,
            2
        ),

        "topic_coverage": round(
            topic_coverage,
            3
        ),

        "topic_score": round(
            topic_score,
            2
        ),

        "matched_topics": matched_topics,

        "missing_topics": missing_topics,

        "relevance_score": relevance_score,

        "relevance_label": label
        
    }