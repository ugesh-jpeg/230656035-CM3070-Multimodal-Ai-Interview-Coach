import librosa
import numpy as np


def _calculate_pause_durations(
    silent_frames: np.ndarray,
    frame_duration: float,
    minimum_pause_duration: float = 0.5
) -> list[float]:
    """
    Convert consecutive silent frames into pause durations.

    Silent regions shorter than 0.5 seconds are ignored because
    they are likely to represent natural gaps between words or
    brief breathing pauses.
    """

    pause_durations: list[float] = []

    current_silent_frames = 0

    for is_silent in silent_frames:

        if is_silent:

            current_silent_frames += 1

        elif current_silent_frames > 0:

            pause_duration = (
                current_silent_frames
                * frame_duration
            )

            if (
                pause_duration
                >= minimum_pause_duration
            ):

                pause_durations.append(
                    pause_duration
                )

            current_silent_frames = 0


    # Handle a pause continuing until the
    # end of the recording.
    if current_silent_frames > 0:

        pause_duration = (
            current_silent_frames
            * frame_duration
        )

        if (
            pause_duration
            >= minimum_pause_duration
        ):

            pause_durations.append(
                pause_duration
            )


    return pause_durations


def analyse_speech(
    audio_path: str,
    word_count: int = 0
) -> dict:
    """
    Extract acoustic and delivery-related features
    from interview audio.

    The analysis includes:
    - response duration;
    - silence ratio;
    - speaking rate;
    - pause count;
    - pause frequency;
    - average pause duration;
    - longest pause duration.

    The speech score is derived from observable
    delivery metrics rather than raw microphone
    amplitude.
    """

    y, sr = librosa.load(
        audio_path,
        sr=None,
        mono=True
    )


    # -----------------------------------
    # Duration
    # -----------------------------------

    duration = float(
        librosa.get_duration(
            y=y,
            sr=sr
        )
    )


    # -----------------------------------
    # Silence detection
    # -----------------------------------

    frame_length = 2048

    hop_length = 512


    rms = librosa.feature.rms(
        y=y,
        frame_length=frame_length,
        hop_length=hop_length
    )[0]


    # RMS is used only to identify
    # low-energy/silent frames.

    silence_threshold = 0.01


    silent_frames = (
        rms < silence_threshold
    )


    total_frames = len(
        rms
    )


    silent_frame_count = int(
        np.sum(
            silent_frames
        )
    )


    if total_frames > 0:

        silence_ratio = (
            silent_frame_count
            / total_frames
        )

    else:

        silence_ratio = 0.0


    # -----------------------------------
    # Pause analysis
    # -----------------------------------

    frame_duration = (
        hop_length
        / sr
    )


    pause_durations = (
        _calculate_pause_durations(
            silent_frames=
                silent_frames,

            frame_duration=
                frame_duration,

            minimum_pause_duration=
                0.5
        )
    )


    pause_count = len(
        pause_durations
    )


    if pause_count > 0:

        average_pause_duration = float(
            np.mean(
                pause_durations
            )
        )

        longest_pause_duration = float(
            np.max(
                pause_durations
            )
        )

    else:

        average_pause_duration = 0.0

        longest_pause_duration = 0.0


    # -----------------------------------
    # Speaking rate and pause frequency
    # -----------------------------------

    if duration > 0:

        duration_minutes = (
            duration
            / 60
        )


        speaking_rate_wpm = (
            word_count
            / duration_minutes
        )


        pause_frequency_per_minute = (
            pause_count
            / duration_minutes
        )

    else:

        speaking_rate_wpm = 0.0

        pause_frequency_per_minute = 0.0


    # -----------------------------------
    # Explainable speech scoring
    # -----------------------------------


    # Speaking rate: maximum 35 points

    if (
        120
        <= speaking_rate_wpm
        <= 170
    ):

        speaking_rate_score = 35

    elif (
        (
            100
            <= speaking_rate_wpm
            < 120
        )
        or
        (
            170
            < speaking_rate_wpm
            <= 180
        )
    ):

        speaking_rate_score = 28

    elif (
        (
            80
            <= speaking_rate_wpm
            < 100
        )
        or
        (
            180
            < speaking_rate_wpm
            <= 200
        )
    ):

        speaking_rate_score = 18

    else:

        speaking_rate_score = 8


    # Silence ratio: maximum 25 points

    if silence_ratio <= 0.35:

        silence_score = 25

    elif silence_ratio <= 0.45:

        silence_score = 18

    elif silence_ratio <= 0.55:

        silence_score = 10

    else:

        silence_score = 4


    # Longest pause: maximum 20 points

    if longest_pause_duration <= 1.5:

        pause_duration_score = 20

    elif longest_pause_duration <= 2.5:

        pause_duration_score = 14

    elif longest_pause_duration <= 4.0:

        pause_duration_score = 7

    else:

        pause_duration_score = 2


    # Pause frequency: maximum 20 points

    if (
        pause_frequency_per_minute
        <= 10
    ):

        pause_frequency_score = 20

    elif (
        pause_frequency_per_minute
        <= 15
    ):

        pause_frequency_score = 15

    elif (
        pause_frequency_per_minute
        <= 20
    ):

        pause_frequency_score = 9

    else:

        pause_frequency_score = 4


    speech_score = (
        speaking_rate_score
        + silence_score
        + pause_duration_score
        + pause_frequency_score
    )


    # -----------------------------------
    # Final result
    # -----------------------------------

    return {

        "duration_seconds":
            round(
                duration,
                2
            ),

        "silence_ratio":
            round(
                silence_ratio,
                2
            ),

        "speaking_rate_wpm":
            round(
                speaking_rate_wpm,
                2
            ),

        "pause_count":
            pause_count,

        "pause_frequency_per_minute":
            round(
                pause_frequency_per_minute,
                2
            ),

        "average_pause_duration":
            round(
                average_pause_duration,
                2
            ),

        "longest_pause_duration":
            round(
                longest_pause_duration,
                2
            ),

        "speech_score":
            round(
                speech_score,
                2
            )
            
    }