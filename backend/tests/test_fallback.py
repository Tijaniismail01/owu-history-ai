from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import MagicMock

# Add project root to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.main import app

client = TestClient(app)

def test_fallback_behavior():
    # Ensure qa_chain is None to trigger fallback
    import backend.main as main_module
    main_module.qa_chain = None
    
    # We need to simulate a case where get_qa_chain returns None (RAG unavailable)
    # or raises an exception during initialization.
    
    original_get_qa_chain = main_module.get_qa_chain
    # Mocking get_qa_chain to return None, which forces fallback to mock_response
    main_module.get_qa_chain = MagicMock(return_value=None)
    
    # Also ensure the global process_query is None so it attempts re-init
    main_module.process_query = None

    try:
        response = client.post("/generate", json={"query": "Abeokuta", "user_age": 25, "education_level": "University", "tone": "Neutral"})
        assert response.status_code == 200
        data = response.json()
        print("Fallback Data:", data)
        # With SimpleSearchAgent, we expect a source type of "Local Record" if data is found
        # OR "System Cache" if even local agent fails (which mock_response does), 
        # but since we have data, SimpleSearchAgent should work.
        
        # Verify we got a response from local agent
        if data["sources"]:
            assert data["sources"][0]["type"] == "Local Record"
            assert "Abeokuta" in str(data["narrative"])
        else:
            # If no data found by local agent, it returns a "No matches" message 
            # but still valid schema.
            assert "searched the archives" in data["narrative"]
    finally:
        # Restore
        main_module.get_qa_chain = original_get_qa_chain
        main_module.process_query = None  # Reset to let it re-init if needed

if __name__ == "__main__":
    test_fallback_behavior()
    print("Fallback Test Passed!")
