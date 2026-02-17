from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

load_dotenv()

from .schemas import NarrativeRequest, NarrativeResponse, TimelineEvent, Source
try:
    from .rag import get_qa_chain
    from .ingest import ingest_documents
except ImportError:
    get_qa_chain = None
    ingest_documents = None

app = FastAPI(title="Owu History GenAI Agent")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global QA Processor
process_query = None

@app.on_event("startup")
async def startup_event():
    global process_query
    if get_qa_chain:
        try:
            # Initialize the RAG processor
            # This might return None if no DB exists yet
            process_query = get_qa_chain()
        except Exception as e:
            print(f"Startup warning: {e}")

@app.post("/generate", response_model=NarrativeResponse)
async def generate_narrative(request: NarrativeRequest):
    global process_query
    
    # Lazy initialization or re-initialization attempt
    if not process_query and get_qa_chain:
         process_query = get_qa_chain()

    # Fallback to SimpleSearchAgent if RAG is unavailable
    if not process_query:
        print("Using SimpleSearchAgent (Local Mode)")
        try:
             # Lazy load global agent to avoid re-initializing on every request if we can help it, 
             # but for now simple instantiation is safer to ensure data freshness or we can make it global too.
             # Let's make it a global for performance if data grows, but local for now is fine.
             from .simple_agent import SimpleSearchAgent
             base_dir = os.path.dirname(os.path.abspath(__file__))
             data_dir = os.path.join(base_dir, "data", "raw")
             local_agent = SimpleSearchAgent(data_dir)
             
             return local_agent.generate(request.query, request.user_age, request.education_level, request.tone)
        except Exception as e:
            print(f"Local Agent Error: {e}")
            return mock_response(request)

    try:
        response = process_query(
            query=request.query,
            age=request.user_age,
            education=request.education_level,
            tone=request.tone
        )
        return response
    except Exception as e:
        print(f"Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def trigger_ingest():
    if ingest_documents:
        try:
            ingest_documents()
            # Re-initialize chain to pick up new data
            global process_query
            if get_qa_chain:
                process_query = get_qa_chain()
            return {"status": "Ingestion triggered and database updated"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
    else:
        raise HTTPException(status_code=503, detail="Ingestion module unavailable")

def mock_response(request: NarrativeRequest) -> NarrativeResponse:
    """Provides a safe fallback response when RAG is offline."""
    return NarrativeResponse(
        narrative="The Owu History Archives are currently initializing. Please try ingesting documents or check back momentarily. (Mock Mode Active)",
        timeline=[
            TimelineEvent(year="14th Century", event="Founding of Owu-Ipole (Mock Data)"),
        ],
        sources=[
             Source(title="System Cache", type="Offline", confidence_score=1.0)
        ],
        metadata={"info": "Running in fallback mode"}
    )

# Serve Frontend (Vite Build)
# We'll point this to the 'dist' folder later
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
elif os.path.exists(os.path.join(os.path.dirname(__file__), "../frontend")):
     # Serve raw frontend for development (no build step needed for simple HTML/JS)
     raw_frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
     print(f"Serving frontend from: {os.path.abspath(raw_frontend_path)}")
     app.mount("/", StaticFiles(directory=raw_frontend_path, html=True), name="frontend")
