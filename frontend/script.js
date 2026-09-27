const API_BASE_URL =
    "http://127.0.0.1:8000";


const analyseBtn =
    document.getElementById("analyseBtn");

const recordBtn =
    document.getElementById("recordBtn");

const stopBtn =
    document.getElementById("stopBtn");

const mediaInput =
    document.getElementById("mediaFile");

const videoPreview =
    document.getElementById("videoPreview");

const recordingStatus =
    document.getElementById("recordingStatus");

const timerDisplay =
    document.getElementById("timer");

const statusText =
    document.getElementById("status");

const questionSelect =
    document.getElementById("questionSelect");

const customQuestionContainer =
    document.getElementById(
        "customQuestionContainer"
    );

const customQuestionInput =
    document.getElementById(
        "customQuestion"
    );


let mediaRecorder;

let recordedChunks = [];

let recordedBlob = null;

let timerInterval = null;

let seconds = 0;

let interviewQuestions = [];


/*
 * Show custom question input when selected.
 */
questionSelect.addEventListener(
    "change",
    () => {

        statusText.textContent = "";

        document
            .getElementById("results")
            .classList
            .add("hidden");


        if (
            questionSelect.value
            === "custom"
        ) {

            customQuestionContainer
                .classList
                .remove("hidden");

            customQuestionInput
                .focus();

        } else {

            customQuestionContainer
                .classList
                .add("hidden");

            customQuestionInput.value = "";
        }
    }
);


/*
 * Start video recording.
 */
recordBtn.addEventListener(
    "click",
    async () => {

        statusText.textContent = "";

        document
            .getElementById("results")
            .classList
            .add("hidden");


        try {

            const stream =
                await navigator.mediaDevices
                    .getUserMedia({

                        audio: true,

                        video: {

                            width: {
                                ideal: 1280
                            },

                            height: {
                                ideal: 720
                            },

                            facingMode: "user"
                        }
                    });


            /*
             * Live camera preview.
             */
            videoPreview.srcObject =
                stream;

            videoPreview.muted =
                true;

            videoPreview.controls =
                false;

            videoPreview
                .classList
                .remove("hidden");

            await videoPreview.play();


            recordedChunks = [];

            recordedBlob = null;

            seconds = 0;

            updateTimer();


            /*
             * Select supported recording format.
             */
            let mimeType = "";


            if (
                MediaRecorder.isTypeSupported(
                    "video/webm;codecs=vp9,opus"
                )
            ) {

                mimeType =
                    "video/webm;codecs=vp9,opus";

            } else if (
                MediaRecorder.isTypeSupported(
                    "video/webm;codecs=vp8,opus"
                )
            ) {

                mimeType =
                    "video/webm;codecs=vp8,opus";

            } else if (
                MediaRecorder.isTypeSupported(
                    "video/webm"
                )
            ) {

                mimeType =
                    "video/webm";
            }


            if (mimeType) {

                mediaRecorder =
                    new MediaRecorder(
                        stream,
                        {
                            mimeType:
                                mimeType
                        }
                    );

            } else {

                mediaRecorder =
                    new MediaRecorder(
                        stream
                    );
            }


            mediaRecorder.ondataavailable =
                event => {

                    if (
                        event.data.size > 0
                    ) {

                        recordedChunks.push(
                            event.data
                        );
                    }
                };


            mediaRecorder.onstop =
                () => {

                    recordedBlob =
                        new Blob(
                            recordedChunks,
                            {
                                type:
                                    mediaRecorder.mimeType
                                    || "video/webm"
                            }
                        );


                    videoPreview.pause();

                    videoPreview.srcObject =
                        null;


                    /*
                     * Playback recorded response.
                     */
                    const videoUrl =
                        URL.createObjectURL(
                            recordedBlob
                        );


                    videoPreview.src =
                        videoUrl;

                    videoPreview.muted =
                        false;

                    videoPreview.controls =
                        true;

                    videoPreview
                        .classList
                        .remove("hidden");


                    recordingStatus
                        .textContent =
                        "Recording complete. "
                        + "You can preview or analyse it.";


                    stream
                        .getTracks()
                        .forEach(
                            track =>
                                track.stop()
                        );
                };


            mediaRecorder.start();


            recordBtn.disabled =
                true;

            stopBtn.disabled =
                false;

            analyseBtn.disabled =
                true;


            recordingStatus
                .textContent =
                "Recording video...";


            startTimer();

        } catch (error) {

            console.error(
                error
            );


            alert(
                "Camera or microphone access was denied "
                + "or is not supported by this browser."
            );
        }
    }
);


/*
 * Stop video recording.
 */
stopBtn.addEventListener(
    "click",
    () => {

        if (
            mediaRecorder
            && mediaRecorder.state
            !== "inactive"
        ) {

            mediaRecorder.stop();
        }


        stopTimer();


        recordBtn.disabled =
            false;

        stopBtn.disabled =
            true;

        analyseBtn.disabled =
            false;
    }
);


/*
 * Handle uploaded video.
 */
mediaInput.addEventListener(
    "change",
    () => {

        statusText.textContent = "";

        document
            .getElementById("results")
            .classList
            .add("hidden");


        if (
            mediaInput.files.length > 0
        ) {

            recordedBlob =
                null;


            const selectedVideo =
                mediaInput.files[0];


            const videoUrl =
                URL.createObjectURL(
                    selectedVideo
                );


            videoPreview.srcObject =
                null;

            videoPreview.src =
                videoUrl;

            videoPreview.muted =
                false;

            videoPreview.controls =
                true;


            videoPreview
                .classList
                .remove("hidden");


            recordingStatus
                .textContent =
                "Uploaded video selected.";


            seconds = 0;

            updateTimer();
        }
    }
);


/*
 * Submit interview response.
 */
analyseBtn.addEventListener(
    "click",
    async () => {

        const question =
            getSelectedQuestion();


        if (!question) {

            alert(
                "Please select an interview question "
                + "or enter a custom question."
            );

            return;
        }


        const selectedFile =
            getSelectedMedia();


        if (!selectedFile) {

            alert(
                "Please upload a video file or record "
                + "a video response."
            );

            return;
        }


        const formData =
            new FormData();


        formData.append(
            "question",
            question
        );


        formData.append(
            "file",
            selectedFile.file,
            selectedFile.filename
        );


        statusText.textContent =
            "Analysing interview response...";


        analyseBtn.disabled =
            true;


        try {

            const response =
                await fetch(
                    `${API_BASE_URL}/analyse`,
                    {
                        method:
                            "POST",

                        body:
                            formData
                    }
                );


            if (!response.ok) {

                const errorText =
                    await response.text();


                throw new Error(
                    `Backend returned `
                    + `${response.status}: `
                    + errorText
                );
            }


            const data =
                await response.json();


            displayResults(
                data,
                question
            );


            if (
                data.feedback_source
                === "ollama"
                ||
                data.feedback_source
                === "ai"
            ) {

                statusText.textContent =
                    "Interview analysis completed "
                    + "with local AI feedback.";

            } else {

                statusText.textContent =
                    "Interview analysis completed "
                    + "using rule-based feedback.";
            }

        } catch (error) {

            console.error(
                error
            );


            statusText.textContent =
                "Error connecting to backend "
                + "or processing interview response.";

        } finally {

            analyseBtn.disabled =
                false;
        }
    }
);


/*
 * Return selected interview question.
 */
function getSelectedQuestion() {

    if (
        questionSelect.value
        === "custom"
    ) {

        return customQuestionInput
            .value
            .trim();
    }


    return questionSelect
        .value
        .trim();
}


/*
 * Return recorded or uploaded video.
 */
function getSelectedMedia() {

    if (recordedBlob) {

        return {

            file:
                recordedBlob,

            filename:
                "live_interview_response.webm"
        };
    }


    if (
        mediaInput.files.length > 0
    ) {

        return {

            file:
                mediaInput.files[0],

            filename:
                mediaInput.files[0].name
        };
    }


    return null;
}


/*
 * Display interview analysis.
 */
function displayResults(
    data,
    submittedQuestion
) {

    document
        .getElementById("results")
        .classList
        .remove("hidden");


    document
        .getElementById(
            "submittedQuestion"
        )
        .textContent =
        submittedQuestion
        || "No question selected.";


    document
        .getElementById(
            "transcript"
        )
        .textContent =
        data.transcript
        || "No transcript available.";


    // -----------------------------------
    // Individual modality scores
    // -----------------------------------

    document
        .getElementById(
            "textScore"
        )
        .textContent =
        formatNumber(
            data.text_analysis
                .text_score
        );


    document
        .getElementById(
            "speechScore"
        )
        .textContent =
        formatNumber(
            data.speech_analysis
                .speech_score
        );


    document
        .getElementById(
            "visualScore"
        )
        .textContent =
        formatNumber(
            data.visual_analysis
                .visual_score
        );


    // -----------------------------------
    // Research comparison:
    // Text-only vs full multimodal
    // -----------------------------------

    document
        .getElementById(
            "textOnlyScore"
        )
        .textContent =
        formatNumber(
            data.fusion
                .text_only_score
        );


    document
        .getElementById(
            "multimodalScore"
        )
        .textContent =
        formatNumber(
            data.fusion
                .multimodal_score
        );


    // -----------------------------------
    // Text metrics
    // -----------------------------------

    document
        .getElementById(
            "wordCount"
        )
        .textContent =
        data.text_analysis
            .word_count
        ?? "-";


    document
        .getElementById(
            "sentenceCount"
        )
        .textContent =
        data.text_analysis
            .sentence_count
        ?? "-";


    document
        .getElementById(
            "fillerWords"
        )
        .textContent =
        data.text_analysis
            .filler_words
        ?? "-";


    document
        .getElementById(
            "lengthScore"
        )
        .textContent =
        formatNumber(
            data.text_analysis
                .length_score,
            0
        );


    document
        .getElementById(
            "structureScore"
        )
        .textContent =
        formatNumber(
            data.text_analysis
                .structure_score,
            0
        );


    document
        .getElementById(
            "clarityScore"
        )
        .textContent =
        formatNumber(
            data.text_analysis
                .clarity_score,
            0
        );


    document
        .getElementById(
            "relevanceScore"
        )
        .textContent =
        formatNumber(
            data.text_analysis
                .relevance_score,
            0
        );


    document
        .getElementById(
            "relevanceLabel"
        )
        .textContent =
        data.text_analysis
            .relevance_label
        || "-";


    // -----------------------------------
    // Speech metrics
    // -----------------------------------

    document
        .getElementById(
            "durationSeconds"
        )
        .textContent =
        `${formatNumber(
            data.speech_analysis
                .duration_seconds,
            2
        )} seconds`;


    document
        .getElementById(
            "speakingRate"
        )
        .textContent =
        `${formatNumber(
            data.speech_analysis
                .speaking_rate_wpm,
            0
        )} WPM`;


    document
        .getElementById(
            "pauseCount"
        )
        .textContent =
        data.speech_analysis
            .pause_count
        ?? "-";


    document
        .getElementById(
            "pauseFrequency"
        )
        .textContent =
        `${formatNumber(
            data.speech_analysis
                .pause_frequency_per_minute,
            0
        )} per minute`;


    document
        .getElementById(
            "averagePause"
        )
        .textContent =
        `${formatNumber(
            data.speech_analysis
                .average_pause_duration,
            2
        )} seconds`;


    document
        .getElementById(
            "longestPause"
        )
        .textContent =
        `${formatNumber(
            data.speech_analysis
                .longest_pause_duration,
            2
        )} seconds`;


    document
        .getElementById(
            "silenceRatio"
        )
        .textContent =
        `${formatNumber(
            data.speech_analysis
                .silence_ratio
                * 100,
            0
        )}%`;


    // -----------------------------------
    // Visual metrics
    // -----------------------------------

    document
        .getElementById(
            "faceDetectionRatio"
        )
        .textContent =
        `${formatNumber(
            data.visual_analysis
                .face_detection_ratio
                * 100,
            0
        )}%`;


    document
        .getElementById(
            "faceCenteredRatio"
        )
        .textContent =
        `${formatNumber(
            data.visual_analysis
                .face_centered_ratio
                * 100,
            0
        )}%`;


    document
        .getElementById(
            "headStability"
        )
        .textContent =
        `${formatNumber(
            data.visual_analysis
                .head_stability
                * 100,
            0
        )}%`;


    document
        .getElementById(
            "sampledFrames"
        )
        .textContent =
        data.visual_analysis
            .sampled_frames
        ?? "-";


    document
        .getElementById(
            "faceDetectedFrames"
        )
        .textContent =
        data.visual_analysis
            .face_detected_frames
        ?? "-";


    // -----------------------------------
    // Performance band
    // -----------------------------------

    document
        .getElementById(
            "performanceBand"
        )
        .textContent =
        data.feedback
            .performance_band
        || "-";


    // -----------------------------------
    // AI coaching summary
    // -----------------------------------

    const aiSummarySection =
        document.getElementById(
            "aiSummarySection"
        );


    const aiSummary =
        document.getElementById(
            "aiSummary"
        );


    if (
        data.ai_feedback?.summary
    ) {

        aiSummary.textContent =
            data.ai_feedback.summary;


        aiSummarySection
            .classList
            .remove("hidden");

    } else {

        aiSummary.textContent =
            "";


        aiSummarySection
            .classList
            .add("hidden");
    }


    // -----------------------------------
    // Rule-based feedback
    // -----------------------------------

    populateList(
        "strengths",
        data.feedback.strengths
    );


    populateList(
        "weaknesses",
        data.feedback.weaknesses
    );


    populateList(
        "improvements",
        data.feedback
            .suggested_improvements
    );
}


/*
 * Format numeric values.
 */
function formatNumber(
    value,
    decimalPlaces = 0
) {

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {

        return "-";
    }


    return Number(
        number.toFixed(
            decimalPlaces
        )
    );
}


/*
 * Populate feedback list.
 */
function populateList(
    elementId,
    items
) {

    const list =
        document.getElementById(
            elementId
        );


    list.innerHTML = "";


    if (
        !Array.isArray(items)
        ||
        items.length === 0
    ) {

        const li =
            document.createElement(
                "li"
            );


        li.textContent =
            "No feedback available "
            + "for this section.";


        list.appendChild(
            li
        );


        return;
    }


    items.forEach(
        item => {

            const li =
                document.createElement(
                    "li"
                );


            li.textContent =
                item;


            list.appendChild(
                li
            );
        }
    );
}


/*
 * Recording timer.
 */
function startTimer() {

    stopTimer();


    timerInterval =
        setInterval(
            () => {

                seconds++;

                updateTimer();

            },
            1000
        );
}


function stopTimer() {

    if (
        timerInterval !== null
    ) {

        clearInterval(
            timerInterval
        );


        timerInterval =
            null;
    }
}


function updateTimer() {

    const mins =
        String(
            Math.floor(
                seconds / 60
            )
        )
        .padStart(
            2,
            "0"
        );


    const secs =
        String(
            seconds % 60
        )
        .padStart(
            2,
            "0"
        );


    timerDisplay.textContent =
        `${mins}:${secs}`;
}


/*
 * Load interview questions.
 */
async function loadInterviewQuestions() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/questions`
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load interview questions."
            );
        }


        interviewQuestions =
            await response.json();


        populateQuestionDropdown();

    } catch (error) {

        console.error(
            error
        );


        questionSelect.innerHTML =
            "";


        const errorOption =
            document.createElement(
                "option"
            );


        errorOption.value =
            "";

        errorOption.textContent =
            "Failed to load questions";


        questionSelect.appendChild(
            errorOption
        );


        const customOption =
            document.createElement(
                "option"
            );


        customOption.value =
            "custom";

        customOption.textContent =
            "Enter a custom question";


        questionSelect.appendChild(
            customOption
        );
    }
}


/*
 * Group questions by category.
 */
function populateQuestionDropdown() {

    questionSelect.innerHTML =
        "";


    const defaultOption =
        document.createElement(
            "option"
        );


    defaultOption.value =
        "";

    defaultOption.textContent =
        "Select a question";


    questionSelect.appendChild(
        defaultOption
    );


    const groupedQuestions =
        {};


    interviewQuestions.forEach(
        item => {

            if (
                !groupedQuestions[
                    item.category
                ]
            ) {

                groupedQuestions[
                    item.category
                ] = [];
            }


            groupedQuestions[
                item.category
            ].push(
                item.question
            );
        }
    );


    Object.entries(
        groupedQuestions
    )
    .forEach(
        (
            [
                category,
                questions
            ]
        ) => {

            const optionGroup =
                document.createElement(
                    "optgroup"
                );


            optionGroup.label =
                category;


            questions.forEach(
                question => {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        question;

                    option.textContent =
                        question;


                    optionGroup.appendChild(
                        option
                    );
                }
            );


            questionSelect.appendChild(
                optionGroup
            );
        }
    );


    const customOption =
        document.createElement(
            "option"
        );


    customOption.value =
        "custom";

    customOption.textContent =
        "Enter a custom question";


    questionSelect.appendChild(
        customOption
    );
}


document.addEventListener(
    "DOMContentLoaded",
    loadInterviewQuestions
);