from app.services.semantic_analysis_service import analyse_relevance
from app.services.text_analysis_service import analyse_text
from app.services.fusion_service import fuse_scores
from app.services.feedback_service import generate_feedback


# ============================================================
# TEST 1
# Text analysis returns the expected scoring information
# ============================================================

def test_text_analysis_returns_score():

    question = "Tell me about yourself."

    transcript = (
        "I am a final year computer science student."
        "I enjoy building AI systems"
        "that solve real world problems."
    )

    relevance = analyse_relevance(
        question,
        transcript
    )

    result = analyse_text(
        transcript,
        relevance
    )

    assert "text_score" in result
    assert "relevance_score" in result
    assert "relevance_label" in result

    assert result["text_score"] >= 0
    assert result["word_count"] > 0


# ============================================================
# TEST 2
# Fusion combines text, speech and visual scores correctly
# ============================================================

def test_fusion_combines_scores():

    result = fuse_scores(
        text_score=70,
        speech_score=50,
        visual_score=80
    )

    assert "text_only_score" in result
    assert "text_speech_score" in result
    assert "multimodal_score" in result

    assert result["text_only_score"] == 70.0

    assert result["text_speech_score"] == 64.0

    assert result["multimodal_score"] == 66.0


# ============================================================
# TEST 3
# Feedback generation returns the expected structure
# ============================================================

def test_feedback_generation():

    text_analysis = {

        "text_score": 72,

        "word_count": 50,

        "sentence_count": 3,

        "filler_words": 0,

        "length_score": 20,

        "structure_score": 18,

        "clarity_score": 18,

        "relevance_score": 35,

        "semantic_similarity": 0.88,

        "relevance_label": "Highly Relevant"
    }

    speech_analysis = {

        "duration_seconds": 30,

        "speech_score": 90,

        "silence_ratio": 0.20,

        "speaking_rate_wpm": 120,

        "pause_count": 3,

        "pause_frequency_per_minute": 6,

        "average_pause_duration": 0.4,

        "longest_pause_duration": 0.9
    }

    visual_analysis = {

        "sampled_frames": 100,

        "face_detected_frames": 100,

        "face_detection_ratio": 1.0,

        "face_centered_ratio": 0.95,

        "head_stability": 0.85,

        "visual_score": 94
    }

    fusion_result = {

        "text_only_score": 72.0,

        "text_speech_score": 77.4,

        "multimodal_score": 81.8
    }

    result = generate_feedback(
        text_analysis,
        speech_analysis,
        visual_analysis,
        fusion_result
    )

    assert "performance_band" in result
    assert "strengths" in result
    assert "weaknesses" in result
    assert "suggested_improvements" in result

    assert result["performance_band"] == "Strong"

    assert any(
        "face" in strength.lower()
        for strength in result["strengths"]
    )


# ============================================================
# TEST 4
# Semantic analysis returns the expected result
# ============================================================

def test_semantic_analysis_returns_result():

    question = "Tell me about yourself."

    transcript = (
        "I am a computer science student."
    )

    result = analyse_relevance(
        question,
        transcript
    )

    assert "semantic_similarity" in result
    assert "relevance_score" in result
    assert "relevance_label" in result


# ============================================================
# TEST 5
# Relevant answer should score higher than unrelated answer
# ============================================================

def test_relevant_answer_scores_higher():

    question = "Tell me about yourself."

    relevant = analyse_relevance(
        question,
        "I am a computer science student"
        "who enjoys AI."
    )

    unrelated = analyse_relevance(
        question,
        "Python uses indentation while Java "
        "uses braces."
    )

    assert (
        relevant["relevance_score"]
        >
        unrelated["relevance_score"]
    )


# ============================================================
# TEST 6
# Poor face centring should generate visual feedback
# ============================================================

def test_off_centre_face_generates_feedback():

    text_analysis = {

        "text_score": 85,

        "word_count": 70,

        "sentence_count": 4,

        "filler_words": 0,

        "length_score": 18,

        "structure_score": 20,

        "clarity_score": 20,

        "relevance_score": 27,

        "semantic_similarity": 0.70,

        "relevance_label": "Moderately Relevant"
    }

    speech_analysis = {

        "duration_seconds": 25,

        "speech_score": 85,

        "silence_ratio": 0.30,

        "speaking_rate_wpm": 150,

        "pause_count": 4,

        "pause_frequency_per_minute": 9,

        "average_pause_duration": 0.7,

        "longest_pause_duration": 1.0
    }

    visual_analysis = {

        "sampled_frames": 150,

        "face_detected_frames": 145,

        "face_detection_ratio": 0.97,

        # Deliberately poor centring
        "face_centered_ratio": 0.10,

        "head_stability": 0.80,

        "visual_score": 60
    }

    fusion_result = fuse_scores(
        text_score=85,
        speech_score=85,
        visual_score=60
    )

    result = generate_feedback(
        text_analysis,
        speech_analysis,
        visual_analysis,
        fusion_result
    )

    assert any(
        "centre" in weakness.lower()
        or "center" in weakness.lower()
        for weakness in result["weaknesses"]
    )

    assert any(
        "centre" in improvement.lower()
        or "center" in improvement.lower()
        for improvement in result[
            "suggested_improvements"
        ]
    )


# ============================================================
# TEST 7
# Low head stability should generate movement feedback
# ============================================================

def test_low_head_stability_generates_feedback():

    text_analysis = {

        "text_score": 85,

        "word_count": 70,

        "sentence_count": 4,

        "filler_words": 0,

        "length_score": 18,

        "structure_score": 20,

        "clarity_score": 20,

        "relevance_score": 27,

        "semantic_similarity": 0.70,

        "relevance_label": "Moderately Relevant"
    }

    speech_analysis = {

        "duration_seconds": 25,

        "speech_score": 85,

        "silence_ratio": 0.30,

        "speaking_rate_wpm": 150,

        "pause_count": 4,

        "pause_frequency_per_minute": 9,

        "average_pause_duration": 0.7,

        "longest_pause_duration": 1.0
    }

    visual_analysis = {

        "sampled_frames": 150,

        "face_detected_frames": 150,

        "face_detection_ratio": 1.0,

        "face_centered_ratio": 0.90,

        # Deliberately unstable
        "head_stability": 0.30,

        "visual_score": 75
    }

    fusion_result = fuse_scores(
        text_score=85,
        speech_score=85,
        visual_score=75
    )

    result = generate_feedback(
        text_analysis,
        speech_analysis,
        visual_analysis,
        fusion_result
    )

    assert any(
        "head" in weakness.lower()
        or "movement" in weakness.lower()
        or "stability" in weakness.lower()
        for weakness in result["weaknesses"]
    )

    assert any(
        "head" in improvement.lower()
        or "movement" in improvement.lower()
        or "stability" in improvement.lower()
        for improvement in result[
            "suggested_improvements"
        ]
    )


# ============================================================
# TEST 8
# Lower visual score should affect multimodal score only,
# while leaving the text-only baseline unchanged
# ============================================================

def test_visual_score_affects_multimodal_fusion():

    strong_visual = fuse_scores(
        text_score=80,
        speech_score=80,
        visual_score=95
    )

    weak_visual = fuse_scores(
        text_score=80,
        speech_score=80,
        visual_score=40
    )

    assert (
        strong_visual["text_only_score"]
        ==
        weak_visual["text_only_score"]
    )

    assert strong_visual["text_only_score"] == 80.0

    assert (
        strong_visual["text_speech_score"]
        ==
        weak_visual["text_speech_score"]
    )

    assert (
        strong_visual["multimodal_score"]
        >
        weak_visual["multimodal_score"]
    )