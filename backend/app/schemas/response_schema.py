from typing import List, Optional

from pydantic import BaseModel


class TextAnalysis(BaseModel):

    text_score: float

    word_count: int

    sentence_count: int

    filler_words: int

    length_score: float

    structure_score: float

    clarity_score: float

    relevance_score: float

    semantic_similarity: float

    relevance_label: str


class SpeechAnalysis(BaseModel):

    duration_seconds: float

    silence_ratio: float

    speaking_rate_wpm: float

    pause_count: int

    pause_frequency_per_minute: float

    average_pause_duration: float

    longest_pause_duration: float

    speech_score: float


class VisualAnalysis(BaseModel):

    sampled_frames: int

    face_detected_frames: int

    face_detection_ratio: float

    face_centered_ratio: float

    head_stability: float

    visual_score: float


class FusionResult(BaseModel):

    text_only_score: float

    text_speech_score: float

    multimodal_score: float


class Feedback(BaseModel):

    performance_band: str

    strengths: List[str]

    weaknesses: List[str]

    suggested_improvements: List[str]


class AIFeedback(BaseModel):

    summary: str


class InterviewAnalysisResponse(BaseModel):

    filename: str

    transcript: str

    text_analysis: TextAnalysis

    speech_analysis: SpeechAnalysis

    visual_analysis: VisualAnalysis

    fusion: FusionResult

    feedback: Feedback

    ai_feedback: Optional[AIFeedback] = None

    feedback_source: str