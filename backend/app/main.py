import json
from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware

from app.utils.file_utils import save_uploaded_file

from app.services.transcription_service import transcribe_audio
from app.services.semantic_analysis_service import analyse_relevance
from app.services.text_analysis_service import analyse_text
from app.services.speech_analysis_service import analyse_speech
from app.services.visual_analysis_service import analyse_visual
from app.services.fusion_service import fuse_scores
from app.services.feedback_service import generate_feedback
from app.services.ai_feedback_service import generate_ai_feedback

from app.schemas.response_schema import (
    InterviewAnalysisResponse
)


app = FastAPI(
    title="Multimodal AI Interview Coach",
    version="0.3.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():

    return {
        "message": "Interview Coach API Running"
    }


@app.get("/questions")
def get_interview_questions():

    questions_file = (
        Path(__file__).resolve().parent
        / "data"
        / "interview_questions.json"
    )

    if not questions_file.exists():

        raise HTTPException(
            status_code=500,
            detail="Interview question bank not found."
        )

    with open(
        questions_file,
        "r",
        encoding="utf-8"
    ) as file:

        questions = json.load(file)

    return questions


@app.post(
    "/analyse",
    response_model=InterviewAnalysisResponse
)
async def analyse_interview(
    question: str = Form(...),
    file: UploadFile = File(...)
):

    """
    Running the complete multimodal interview analysis pipeline.

    The uploaded response is processed using:
    - Whisper transcription;
    - semantic and rule-based text analysis;
    - Librosa speech analysis;
    - MediaPipe visual analysis;
    - weighted late fusion;
    - deterministic coaching feedback;
    - an optional Ollama-generated coaching summary.
    """

    question = question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Interview question is required."
        )

    # -----------------------------------
    # Find expected answer template
    # -----------------------------------

    questions_file = (
        Path(__file__).resolve().parent
        / "data"
        / "interview_questions.json"
    )

    if not questions_file.exists():

        raise HTTPException(
            status_code=500,
            detail="Interview question bank not found."
        )

    with open(
        questions_file,
        "r",
        encoding="utf-8"
    ) as question_file:

        question_bank = json.load(
            question_file
        )

    reference_text = question

    expected_topics = []

    for item in question_bank:

        if item["question"] == question:

            reference_text = item.get(
                "expected_answer",
                question
            )

            expected_topics = item.get(
                "expected_topics",
                []
            )

            break

    # -----------------------------------
    # Validate uploaded media
    # -----------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail=(
                "Interview response file "
                "is required."
            )
        )

    # -----------------------------------
    # Save uploaded interview media
    # -----------------------------------

    file_path = save_uploaded_file(
        file
    )

    # -----------------------------------
    # Whisper transcription
    # -----------------------------------

    transcript = transcribe_audio(
        file_path
    )

    # -----------------------------------
    # Semantic analysis
    # -----------------------------------

    relevance_result = analyse_relevance(
        reference_text,
        transcript,
        expected_topics
    )

    # -----------------------------------
    # Text analysis
    # -----------------------------------

    text_analysis = analyse_text(
        transcript,
        relevance_result
    )

    # -----------------------------------
    # Speech analysis
    # -----------------------------------

    speech_analysis = analyse_speech(
        file_path,
        text_analysis["word_count"]
    )

    # -----------------------------------
    # Visual analysis
    # -----------------------------------

    visual_analysis = analyse_visual(
        file_path
    )

    # -----------------------------------
    # Multimodal analysis
    # -----------------------------------

    fusion_result = fuse_scores(
        text_analysis["text_score"],
        speech_analysis["speech_score"],
        visual_analysis["visual_score"]
    )

    # -----------------------------------
    # Rule-based feedback
    # -----------------------------------

    feedback = generate_feedback(
        text_analysis,
        speech_analysis,
        visual_analysis,
        fusion_result
    )

    # -----------------------------------
    # AI coaching summary
    # -----------------------------------

    try:

        ai_feedback = generate_ai_feedback(
            question=question,
            transcript=transcript,
            text_analysis=text_analysis,
            speech_analysis=speech_analysis,
            visual_analysis=visual_analysis,
            fusion_result=fusion_result,
            rule_based_feedback=feedback
        )

        feedback_source = "ollama"

    except Exception:

        ai_feedback = None
        feedback_source = "rule_based"

    # -----------------------------------
    # Final response
    # -----------------------------------

    return {

        "filename":
            file.filename,

        "transcript":
            transcript,

        "text_analysis":
            text_analysis,

        "speech_analysis":
            speech_analysis,

        "visual_analysis":
            visual_analysis,

        "fusion":
            fusion_result,

        "feedback":
            feedback,

        "ai_feedback":
            ai_feedback,

        "feedback_source":
            feedback_source
    }