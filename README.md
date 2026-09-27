# Multimodal AI Interview Coach

A single-response interview practice prototype that analyses answer content, speech delivery, and observable visual features. It combines these results to generate structured coaching feedback and displays a text-only comparison.

## Components

- FastAPI backend and HTML/CSS/JavaScript frontend
- Whisper for speech transcription
- Rule-based text analysis and Sentence-BERT for semantic relevance
- Librosa for speaking rate, pauses, and silence
- MediaPipe for observable visual measures
- Ollama (`llama3.1:8b`) for a coaching summary

## Requirements

Python 3.11, Ollama, and the packages in `backend/requirements.txt`. Browser recording requires camera and microphone access.

## Run locally

From the project folder, set up Python:

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install Ollama separately and download the model:

```bash
ollama pull llama3.1:8b
```

From the `backend` folder, start the API:

```bash
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Its interactive documentation is at `http://127.0.0.1:8000/docs`.

In another Terminal window, start the frontend:

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://localhost:5500` in your browser. Select a question, record an answer or upload an existing recording, and analyse it.

## Tests

With the virtual environment active, run this from the `backend` folder:

```bash
pytest
```

## Data and limitations

Question definitions are stored in `backend/app/data/interview_questions.json`. Uploaded responses and local environment files are excluded from Git.

This is a single-response research prototype. Its visual measures describe observable face position and movement; they do not determine emotion, personality, or eye contact. Scoring thresholds and fusion weights are manually defined.
