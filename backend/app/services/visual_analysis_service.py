import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path


mp_face_mesh = mp.solutions.face_mesh


def _calculate_head_stability(
    nose_positions: list[tuple[float, float]]
) -> float:
    """
    Estimate head-position stability using movement of the
    approximate nose landmark across sampled video frames.

    Higher values indicate less positional movement.
    """

    if len(nose_positions) < 2:
        return 0.0

    positions = np.array(
        nose_positions,
        dtype=np.float32
    )

    differences = np.diff(
        positions,
        axis=0
    )

    movement = np.linalg.norm(
        differences,
        axis=1
    )

    average_movement = float(
        np.mean(movement)
    )

    movement_limit = 0.05

    stability_score = max(
        0.0,
        1.0 - (
            average_movement
            / movement_limit
        )
    )

    stability_score = min(
        stability_score,
        1.0
    )

    return round(
        stability_score,
        3
    )


def _calculate_visual_score(
    face_detection_ratio: float,
    face_centered_ratio: float,
    head_stability: float
) -> float:
    """
    Produce a simple explainable visual score.

    Weighting:
        Face visibility      : 40%
        Face centred         : 30%
        Head stability       : 30%
    """

    score = (
        (0.40 * face_detection_ratio)
        + (0.30 * face_centered_ratio)
        + (0.30 * head_stability)
    ) * 100

    return round(
        score,
        2
    )


def analyse_visual(
    video_path: str,
    sample_every_n_frames: int = 5
) -> dict:
    """
    Analyse observable visual behaviour from interview video.

    Current metrics:
        - face detection ratio
        - face centred ratio
        - head-position stability
        - visual score

    No attempt is made to infer emotion, confidence,
    personality or psychological state.
    """

    video_file = Path(
        video_path
    )

    if not video_file.exists():
        raise FileNotFoundError(
            f"Video file not found: {video_path}"
        )

    capture = cv2.VideoCapture(
        str(video_file)
    )

    if not capture.isOpened():
        raise RuntimeError(
            f"Unable to open video: {video_path}"
        )

    total_sampled_frames = 0
    detected_face_frames = 0
    centered_face_frames = 0

    nose_positions = []

    frame_index = 0

    try:

        with mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as face_mesh:

            while True:

                success, frame = (
                    capture.read()
                )

                if not success:
                    break

                frame_index += 1

                if (
                    frame_index
                    % sample_every_n_frames
                    != 0
                ):
                    continue

                total_sampled_frames += 1

                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                results = (
                    face_mesh.process(
                        rgb_frame
                    )
                )

                if (
                    not results
                    .multi_face_landmarks
                ):
                    continue

                detected_face_frames += 1

                face_landmarks = (
                    results
                    .multi_face_landmarks[0]
                    .landmark
                )

                # MediaPipe Face Mesh landmark 1 is
                # near the nose region.
                nose = face_landmarks[1]

                nose_x = float(
                    nose.x
                )

                nose_y = float(
                    nose.y
                )

                nose_positions.append(
                    (
                        nose_x,
                        nose_y
                    )
                )

                if (
                    0.30 <= nose_x <= 0.70
                    and
                    0.25 <= nose_y <= 0.75
                ):
                    centered_face_frames += 1

    finally:

        capture.release()

    if total_sampled_frames > 0:

        face_detection_ratio = (
            detected_face_frames
            / total_sampled_frames
        )

    else:

        face_detection_ratio = 0.0

    if detected_face_frames > 0:

        face_centered_ratio = (
            centered_face_frames
            / detected_face_frames
        )

    else:

        face_centered_ratio = 0.0

    head_stability = (
        _calculate_head_stability(
            nose_positions
        )
    )

    visual_score = (
        _calculate_visual_score(
            face_detection_ratio,
            face_centered_ratio,
            head_stability
        )
    )

    return {

        "sampled_frames":
            total_sampled_frames,

        "face_detected_frames":
            detected_face_frames,

        "face_detection_ratio":
            round(
                face_detection_ratio,
                3
            ),

        "face_centered_ratio":
            round(
                face_centered_ratio,
                3
            ),

        "head_stability":
            head_stability,

        "visual_score":
            visual_score

    }