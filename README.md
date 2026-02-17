# Owu History GenAI System

An intelligent agent for generating personalized, source-verified historical narratives of the Owu people.

## Features

- **Personalised Narratives**: Adjusts content based on user age and education level.
- **Local Search Agent**: Searches through local text files to answer questions without external APIs.
- **Owu Oriki Retrieval**: Specialized support for retrieving and presenting Owu praise poetry (Oriki), including fuzzy search for names (e.g., "Ajiboshin" -> "Ajibosin").
- **RAG Architecture**: Uses Retrieval-Augmented Generation to ground answers in verified documents.
- **Source Verification**: Citations provided for every generation.

## Prerequisites

- **Python 3.9+**: Required for the backend.
- **OpenAI API Key**: Required for the LLM and Embeddings (for GenAI mode).
- **No Key Required**: For Local Search Agent mode.

## Setup Instructions

### 1. Backend Setup

Navigate to the `backend` directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory with your API key:

```env
OPENAI_API_KEY=your_sk_key_here
```

start the server:

```bash
uvicorn main:app --reload
```

### 2. Frontend Setup

The frontend is served directly by the FastAPI backend for simplicity.
Just open your browser to:
`http://localhost:8000`

### 3. Adding Data

To verify the system with real data:

1. Place text files (`.txt`) containing Owu history in `backend/data/raw`.
2. Trigger ingestion by restarting the server or calling the ingest endpoint.

## Troubleshooting

If you see "Python was not found", you must install Python from [python.org](https://www.python.org/downloads/) and ensure it is added to your PATH.
