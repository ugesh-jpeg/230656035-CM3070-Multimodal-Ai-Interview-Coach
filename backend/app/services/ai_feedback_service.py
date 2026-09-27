import json

from ollama import chat
from pydantic import BaseModel, Field


OLLAMA_MODEL = "llama3.1:8b"


class AIFeedbackResult(BaseModel):
    summary: str = Field(
        min_length=20,
        max_length=1000
    )


def generate_ai_feedback(
    question: str,
    transcript: str,
    text_analysis: dict,
    speech_analysis: dict,
    visual_analysis: dict,
    fusion_result: dict,
    rule_based_feedback: dict
) -> dict:
    """
    Generate a concise multimodal coaching summary using
    the locally hosted Ollama model.

    The deterministic analysis pipeline remains responsible for:
    - text, speech and visual scores;
    - multimodal fusion;
    - performance band;
    - strengths;
    - weaknesses;
    - suggested improvements.

    Ollama only converts verified evidence into a
    natural-language coaching summary.
    """

    analysis_payload = {

        "interview_question":
            question,

        "transcript":
            transcript,

        "scores": {

            "text_score":
                text_analysis[
                    "text_score"
                ],

            "speech_score":
                speech_analysis[
                    "speech_score"
                ],

            "visual_score":
                visual_analysis[
                    "visual_score"
                ],

            "text_only_score":
                fusion_result[
                    "text_only_score"
                ],

            "multimodal_score":
                fusion_result[
                    "multimodal_score"
                ]
        },

        "performance_band":
            rule_based_feedback[
                "performance_band"
            ],

        "verified_strengths":
            rule_based_feedback[
                "strengths"
            ],

        "verified_weaknesses":
            rule_based_feedback[
                "weaknesses"
            ],

        "verified_suggested_improvements":
            rule_based_feedback[
                "suggested_improvements"
            ],

        "supporting_metrics": {

            "text": {

                "word_count":
                    text_analysis[
                        "word_count"
                    ],

                "sentence_count":
                    text_analysis[
                        "sentence_count"
                    ],

                "filler_words":
                    text_analysis[
                        "filler_words"
                    ],

                "relevance_score":
                    text_analysis[
                        "relevance_score"
                    ],

                "relevance_label":
                    text_analysis[
                        "relevance_label"
                    ]
            },

            "speech": {

                "speaking_rate_wpm":
                    speech_analysis[
                        "speaking_rate_wpm"
                    ],

                "pause_count":
                    speech_analysis[
                        "pause_count"
                    ],

                "pause_frequency_per_minute":
                    speech_analysis[
                        "pause_frequency_per_minute"
                    ],

                "average_pause_duration":
                    speech_analysis[
                        "average_pause_duration"
                    ],

                "longest_pause_duration":
                    speech_analysis[
                        "longest_pause_duration"
                    ],

                "silence_ratio":
                    speech_analysis[
                        "silence_ratio"
                    ]
            },

            "visual": {

                "face_detection_ratio":
                    visual_analysis[
                        "face_detection_ratio"
                    ],

                "face_centered_ratio":
                    visual_analysis[
                        "face_centered_ratio"
                    ],

                "head_stability":
                    visual_analysis[
                        "head_stability"
                    ]
            }
        }
    }


    system_prompt = (
        "You are an interview coaching assistant. "

        "Write one concise and constructive multimodal coaching "
        "summary using only the supplied verified evidence. "

        "The deterministic system has already calculated all "
        "scores, strengths, weaknesses and suggested improvements. "
        "Do not calculate, modify or reinterpret any score. "

        "Do not change the performance band. "

        "Use the supplied verified strengths, weaknesses and suggested "
        "improvements as the authoritative source for coaching claims. "
        "Preserve their meaning rather than generalising them into broader "
        "judgements. "

        "The summary must include at least one verified textual observation, "
        "one verified speech observation and one verified visual observation "
        "when evidence from all three modalities is available. "

        "For speech, describe the verified measurement directly. "
        "For example, say 'your speaking rate was within the preferred "
        "range' or 'your pauses were generally brief'. "
        "Never summarise speech measurements using phrases such as "
        "'excellent speaking skills', 'good speaking skills', "
        "'strong speaking skills', 'communication skills', "
        "'verbal communication skills' or similar broad evaluations. "

        "For visual behaviour, only discuss whether the face "
        "remained visible, whether it remained centred within the "
        "camera frame, and head-position stability. "

        "Do not claim that eye contact, gaze direction, facial "
        "expression, posture, gestures or speaking volume were "
        "measured. "

        "Do not infer confidence, nervousness, emotion, personality, "
        "enthusiasm, professionalism, honesty, competence or other "
        "psychological characteristics. "

        "Do not generalise specific measurements into broader qualities. "
        "For example, do not describe acceptable speaking rate or pause "
        "behaviour as 'good verbal communication', 'effective communication' "
        "or 'strong communication skills'. Do not describe face visibility, "
        "centring or head stability as 'good visual presence' or similar "
        "general qualities. State the measured observation directly instead. "

        "Do not invent strengths, weaknesses, behaviours or "
        "measurements. "

        "The summary should be approximately three to five "
        "sentences. "

        "Mention the overall performance, important verified "
        "strengths across the available modalities, and the most "
        "important verified area for improvement when one exists. "

        "If there are no verified weaknesses, do not invent one. "

        "Address the interviewee directly using 'you' and maintain "
        "an encouraging professional tone."
    )


    response = chat(
        model=OLLAMA_MODEL,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": json.dumps(
                    analysis_payload,
                    ensure_ascii=False
                )
            }
        ],

        format=
            AIFeedbackResult
            .model_json_schema(),

        options={
            "temperature": 0.2
        }
    )


    response_content = (
        response.message.content
    )


    if not response_content:

        raise RuntimeError(
            "Ollama returned an empty "
            "feedback response."
        )


    try:

        parsed_feedback = (
            AIFeedbackResult
            .model_validate_json(
                response_content
            )
        )

    except Exception as exc:

        raise RuntimeError(
            "Ollama returned feedback that "
            "did not match the required schema."
        ) from exc


    return (
        parsed_feedback
        .model_dump()
    )