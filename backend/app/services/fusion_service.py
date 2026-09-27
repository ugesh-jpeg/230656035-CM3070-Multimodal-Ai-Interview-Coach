def fuse_scores(
    text_score: float,
    speech_score: float,
    visual_score: float
) -> dict:
    """
    Calculate scores for the three evaluation configurations.

    Configuration A:
        Text only

    Configuration B:
        Text + Speech
        70% Text + 30% Speech

    Configuration C:
        Full Multimodal
        50% Text + 30% Speech + 20% Visual
    """

    text_only_score = round(
        text_score,
        2
    )

    text_speech_score = round(
        (0.70 * text_score)
        + (0.30 * speech_score),
        2
    )

    multimodal_score = round(
        (0.50 * text_score)
        + (0.30 * speech_score)
        + (0.20 * visual_score),
        2
    )

    return {
        "text_only_score":
            text_only_score,

        "text_speech_score":
            text_speech_score,

        "multimodal_score":
            multimodal_score
            
    }