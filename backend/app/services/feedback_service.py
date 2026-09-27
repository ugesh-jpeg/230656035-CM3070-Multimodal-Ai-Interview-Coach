def generate_feedback(
    text_analysis: dict,
    speech_analysis: dict,
    visual_analysis: dict,
    fusion_result: dict
) -> dict:
    """
    Generate explainable multimodal interview coaching feedback
    using text, speech and visual behavioural metrics.

    Feedback is restricted to observable or directly calculated
    metrics. The system does not infer confidence, emotion,
    personality or other psychological characteristics.
    """

    strengths = []
    weaknesses = []
    improvements = []

    # --------------------------------------------------
    # Extract text metrics
    # --------------------------------------------------

    text_score = text_analysis.get(
        "text_score",
        0
    )

    filler_words = text_analysis.get(
        "filler_words",
        0
    )

    relevance_score = text_analysis.get(
        "relevance_score",
        0
    )

    # --------------------------------------------------
    # Extract speech metrics
    # --------------------------------------------------

    speaking_rate = speech_analysis.get(
        "speaking_rate_wpm",
        0
    )

    pause_count = speech_analysis.get(
        "pause_count",
        0
    )

    pause_frequency = speech_analysis.get(
        "pause_frequency_per_minute",
        0
    )

    longest_pause_duration = speech_analysis.get(
        "longest_pause_duration",
        0
    )

    silence_ratio = speech_analysis.get(
        "silence_ratio",
        0
    )

    # --------------------------------------------------
    # Extract visual metrics
    # --------------------------------------------------

    face_detection_ratio = visual_analysis.get(
        "face_detection_ratio",
        0
    )

    face_centered_ratio = visual_analysis.get(
        "face_centered_ratio",
        0
    )

    head_stability = visual_analysis.get(
        "head_stability",
        0
    )

    # --------------------------------------------------
    # Extract multimodal score
    # --------------------------------------------------

    combined_score = fusion_result.get(
        "multimodal_score",
        0
    )


    # ==================================================
    # TEXT FEEDBACK
    # ==================================================


    # --------------------------------------------------
    # Question relevance
    # --------------------------------------------------

    if relevance_score >= 29:

        strengths.append(
            "The response remained highly relevant "
            "to the interview question."
        )

    elif relevance_score >= 20:

        strengths.append(
            "The response generally addressed "
            "the interview question."
        )

        improvements.append(
            "Continue linking each example directly "
            "back to the interview question."
        )

    elif relevance_score >= 10:

        weaknesses.append(
            "Parts of the response drifted away "
            "from the interview question."
        )

        improvements.append(
            "Stay focused on the key requirement "
            "of the question throughout the answer."
        )

    else:

        weaknesses.append(
            "The response did not consistently "
            "address the interview question."
        )

        improvements.append(
            "Before answering, identify the main "
            "requirement of the question and ensure "
            "each point directly supports it."
        )


    # --------------------------------------------------
    # Text quality
    # --------------------------------------------------

    if text_score >= 70:

        strengths.append(
            "The response was well developed "
            "and appropriately structured."
        )

    elif text_score >= 50:

        strengths.append(
            "The response demonstrated a reasonable "
            "level of organisation."
        )

        improvements.append(
            "Develop each point with slightly more "
            "supporting detail."
        )

    else:

        weaknesses.append(
            "The response could be developed with "
            "more detail and structure."
        )

        improvements.append(
            "Use a clear structure such as the STAR "
            "method when describing experiences."
        )


    # --------------------------------------------------
    # Filler words
    # --------------------------------------------------

    if filler_words == 0:

        strengths.append(
            "No filler words were detected."
        )

    elif filler_words <= 2:

        strengths.append(
            "Only a small number of filler words "
            "were detected."
        )

    else:

        weaknesses.append(
            f"The response contained "
            f"{filler_words} filler words."
        )

        improvements.append(
            "Replace filler words with short, "
            "intentional pauses."
        )


    # ==================================================
    # SPEECH FEEDBACK
    # ==================================================


    # --------------------------------------------------
    # Speaking rate
    # --------------------------------------------------

    if speaking_rate == 0:

        weaknesses.append(
            "The speaking rate could not be "
            "reliably calculated."
        )

    elif 120 <= speaking_rate <= 170:

        strengths.append(
            "The speaking rate was within the "
            "preferred range."
        )

    elif 100 <= speaking_rate < 120:

        weaknesses.append(
            f"The speaking rate was approximately "
            f"{speaking_rate:.0f} words per minute, "
            "which was slightly slower than the "
            "preferred range."
        )

        improvements.append(
            "Practise delivering responses at a "
            "slightly quicker and more consistent pace."
        )

    elif 170 < speaking_rate <= 180:

        weaknesses.append(
            f"The speaking rate was approximately "
            f"{speaking_rate:.0f} words per minute, "
            "which was slightly faster than the "
            "preferred range."
        )

        improvements.append(
            "Slow the delivery slightly so important "
            "points are easier to follow."
        )

    elif speaking_rate < 100:

        weaknesses.append(
            f"The speaking rate was approximately "
            f"{speaking_rate:.0f} words per minute, "
            "which was relatively slow."
        )

        improvements.append(
            "Practise answering with a more continuous "
            "speaking rhythm while maintaining clarity."
        )

    else:

        weaknesses.append(
            f"The speaking rate was approximately "
            f"{speaking_rate:.0f} words per minute, "
            "which was relatively fast."
        )

        improvements.append(
            "Reduce the speaking rate to make the "
            "response easier to follow."
        )


    # --------------------------------------------------
    # Longest pause
    # --------------------------------------------------

    if longest_pause_duration == 0:

        strengths.append(
            "No extended pauses were detected."
        )

    elif longest_pause_duration <= 1.5:

        strengths.append(
            "The detected pauses were generally "
            "brief and natural."
        )

    elif longest_pause_duration <= 2.5:

        weaknesses.append(
            f"The longest pause lasted approximately "
            f"{longest_pause_duration:.1f} seconds "
            "and slightly interrupted the flow."
        )

        improvements.append(
            "Prepare the next key point before "
            "finishing the current one to maintain "
            "a smoother response."
        )

    elif longest_pause_duration <= 4:

        weaknesses.append(
            f"A long pause of approximately "
            f"{longest_pause_duration:.1f} seconds "
            "interrupted the response."
        )

        improvements.append(
            "Outline the main points before answering "
            "to reduce extended hesitations."
        )

    else:

        weaknesses.append(
            f"The response contained an extended "
            f"pause of approximately "
            f"{longest_pause_duration:.1f} seconds."
        )

        improvements.append(
            "Use a brief planning pause before "
            "starting the response and organise "
            "the answer into clear sections."
        )


    # --------------------------------------------------
    # Pause frequency
    # --------------------------------------------------

    if pause_count == 0:

        strengths.append(
            "The response contained no detected "
            "extended pauses."
        )

    elif pause_frequency <= 10:

        strengths.append(
            "The frequency of pauses was within "
            "the preferred range."
        )

    elif pause_frequency <= 15:

        weaknesses.append(
            "Pauses occurred somewhat frequently "
            "during the response."
        )

        improvements.append(
            "Practise smoother transitions between "
            "ideas to reduce unnecessary pauses."
        )

    elif pause_frequency <= 20:

        weaknesses.append(
            "Frequent pauses affected the continuity "
            "of the response."
        )

        improvements.append(
            "Practise connecting key points into "
            "longer, more continuous sentences."
        )

    else:

        weaknesses.append(
            "A high frequency of pauses disrupted "
            "the flow of the response."
        )

        improvements.append(
            "Plan the main points before answering "
            "and practise transitions between them."
        )


    # --------------------------------------------------
    # Silence ratio
    # --------------------------------------------------

    if silence_ratio <= 0.35:

        strengths.append(
            "The proportion of silence was within "
            "the preferred range."
        )

    elif silence_ratio <= 0.45:

        weaknesses.append(
            "The response contained a moderately "
            "high proportion of silence."
        )

        improvements.append(
            "Aim for a more continuous delivery while "
            "keeping pauses purposeful."
        )

    elif silence_ratio <= 0.55:

        weaknesses.append(
            "A relatively high proportion of the "
            "response consisted of silence."
        )

        improvements.append(
            "Practise maintaining a smoother speaking "
            "rhythm with shorter pauses."
        )

    else:

        weaknesses.append(
            "A substantial proportion of the response "
            "consisted of silence."
        )

        improvements.append(
            "Prepare a simple response structure before "
            "speaking to reduce long periods of silence."
        )


    # ==================================================
    # VISUAL FEEDBACK
    # ==================================================


    # --------------------------------------------------
    # Face visibility
    # --------------------------------------------------

    if face_detection_ratio >= 0.90:

        strengths.append(
            "Your face remained consistently visible "
            "within the camera frame."
        )

    elif face_detection_ratio >= 0.70:

        weaknesses.append(
            "Your face was not visible for part of "
            "the response."
        )

        improvements.append(
            "Remain within the camera frame throughout "
            "the response so your visual behaviour can "
            "be assessed consistently."
        )

    else:

        weaknesses.append(
            "Your face was frequently not visible "
            "within the camera frame."
        )

        improvements.append(
            "Position the camera so your face remains "
            "clearly visible throughout the response."
        )


    # --------------------------------------------------
    # Face centring
    # --------------------------------------------------

    if face_detection_ratio >= 0.50:

        if face_centered_ratio >= 0.80:

            strengths.append(
                "Your face remained well positioned "
                "within the camera frame."
            )

        elif face_centered_ratio >= 0.50:

            weaknesses.append(
                "Your face moved away from the centre "
                "of the camera frame at times."
            )

            improvements.append(
                "Try to maintain a more central position "
                "relative to the camera."
            )

        else:

            weaknesses.append(
                "Your face was frequently positioned "
                "away from the centre of the camera frame."
            )

            improvements.append(
                "Adjust your seating or camera position "
                "so your face remains closer to the "
                "centre of the frame."
            )


    # --------------------------------------------------
    # Head stability
    # --------------------------------------------------

    if face_detection_ratio >= 0.50:

        if head_stability >= 0.80:

            strengths.append(
                "Your head position remained relatively "
                "stable during the response."
            )

        elif head_stability >= 0.50:

            weaknesses.append(
                "Some noticeable head movement was "
                "detected during the response."
            )

            improvements.append(
                "Try to reduce unnecessary head movement "
                "while maintaining natural behaviour."
            )

        else:

            weaknesses.append(
                "Frequent head movement reduced visual "
                "stability during the response."
            )

            improvements.append(
                "Maintain a steadier head position and "
                "reduce large or repeated movements "
                "during the response."
            )


    # ==================================================
    # PERFORMANCE BAND
    # ==================================================

    if combined_score >= 70:

        performance_band = "Strong"

    elif combined_score >= 50:

        performance_band = "Moderate"

    else:

        performance_band = "Needs Improvement"


    return {

        "performance_band":
            performance_band,

        "strengths":
            strengths,

        "weaknesses":
            weaknesses,

        "suggested_improvements":
            improvements

    }