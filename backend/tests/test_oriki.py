import sys
import os
import unittest

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.stdout.reconfigure(encoding='utf-8')

from backend.simple_agent import SimpleSearchAgent

class TestOrikiRetrieval(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(base_dir, "../data/raw")
        self.agent = SimpleSearchAgent(self.data_dir)

    def test_retrieve_ajibosin_oriki(self):
        print("\nTesting 'Ajibosin' query...")
        response = self.agent.generate("Ajibosin", 25, "General", "Neutral")
        print(f"Narrative match: {response.narrative[:100]}...")
        
        # Check for Yoruba lyrics specific to Ajibosin
        # "Owu l’ákọ́dá oooo" is common, but "Ọmọ Arowíyì ní ń jóyè" is specific
        self.assertTrue("Ajibosin" in response.narrative or "Ajíbọ̀sìn" in response.narrative, "Should contain the name")
        # Check if it prioritized the Oriki section (which has Yoruba text)
        # We expect some Yoruba words like 'Ọmọ'
        self.assertTrue("Ọmọ" in response.narrative, "Should contain Yoruba praise words")

    def normalize_text(self, text):
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn').lower()

    def test_retrieve_ajibosin_misspelling(self):
        print("\nTesting 'Oriki Ajiboshin' (misspelled) query...")
        response = self.agent.generate("Give me the Oriki of Ajiboshin", 25, "General", "Neutral")
        print(f"Top results: {[s.title for s in response.sources]}")
        # Should still find Ajibosin despite 'sh' vs 's'
        normalized_narrative = self.normalize_text(response.narrative)
        self.assertTrue("ajibosin" in normalized_narrative, "Should find Ajibosin even with 'Ajiboshin' query")
        # Check that the specific Ajibosin section is retrieved (checking for title part)
        self.assertTrue("3. oriki ajibosin" in normalized_narrative or "lineage praise" in normalized_narrative, 
                        "Should retrieve the specific Ajibosin Oriki section")

    def test_retrieve_general_oriki(self):
        print("\nTesting 'Oriki Owu' query...")
        response = self.agent.generate("Give me the Oriki of Owu", 25, "General", "Neutral")
        print(f"Narrative match id: {response.narrative[:100]}...")
        # Should contain "Owu l’ákọ́dá"
        # Normalize both to ensure match despite accent encoding differences
        normalized_narrative = self.normalize_text(response.narrative)
        self.assertTrue("akoda" in normalized_narrative, "Should contain 'akoda' (normalized from ákọ́dá)")

if __name__ == "__main__":
    unittest.main()
