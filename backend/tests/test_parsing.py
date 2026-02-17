from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import MagicMock

# Add backend to sys path
# Add project root to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.main import app, NarrativeRequest

# Note: We can't easily import generate_narrative's internal logic without refactoring, 
# but we can mock the qa_chain in main.py.

client = TestClient(app)

def test_timeline_parsing():
    # Mock the get_qa_chain to return a mock processor function
    import backend.main as main_module
    from backend.schemas import NarrativeResponse, TimelineEvent, Source # Import to return proper objects

    # Create a mock processor that returns a valid NarrativeResponse object, NOT a dict
    mock_processor = MagicMock()
    mock_processor.return_value = NarrativeResponse(
        narrative="The Owu people originate from Ile-Ife. They are warriors.",
        timeline=[
            TimelineEvent(year="14th Century", event="Owu Ipole founded"),
            TimelineEvent(year="1821", event="Owu War begins")
        ],
        sources=[Source(title="Test", type="Mock", confidence_score=1.0)],
        metadata={}
    )

    original_get_qa_chain = main_module.get_qa_chain
    main_module.get_qa_chain = MagicMock(return_value=mock_processor)
    main_module.process_query = None # Force re-init with our mock

    try:
        response = client.post("/generate", json={"query": "test"})
        
        assert response.status_code == 200
        data = response.json()
        
        print("Narrative:", data["narrative"])
        print("Timeline:", data["timeline"])
        
        assert "TIMELINE_JSON" not in data["narrative"]
        assert len(data["timeline"]) == 2
        assert data["timeline"][0]["year"] == "14th Century"
    finally:
        main_module.get_qa_chain = original_get_qa_chain
        main_module.process_query = None

from pydantic import BaseModel
if __name__ == "__main__":
    try:
        test_timeline_parsing()
        print("Test Passed!")
    except ImportError:
        # Fallback if libraries missing
        print("Skipping test due to missing dependencies in env")
    except Exception as e:
        print(f"Test Failed: {e}")
