import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.simple_agent import SimpleSearchAgent

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "../data/raw")

print(f"Testing with data dir: {data_dir}")
agent = SimpleSearchAgent(data_dir)
response = agent.generate("Abeokuta", 25, "General", "Neutral")
print("Narrative:", response.narrative)
print("Timeline:", response.timeline)
