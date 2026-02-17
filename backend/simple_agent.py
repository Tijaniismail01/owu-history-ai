import os
import re
import unicodedata
import difflib
from typing import List, Dict
from typing import Optional
from .schemas import NarrativeResponse, TimelineEvent, Source

class SimpleSearchAgent:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.documents = []
        self.load_data()

    def load_data(self):
        """Reads all .txt files in the data directory."""
        self.documents = []
        if not os.path.exists(self.data_dir):
            print(f"Data directory {self.data_dir} not found.")
            return

        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(".txt"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            text = f.read()
                            # Split by double newlines to get paragraphs roughly
                            paragraphs = text.split("\n\n")
                            for p in paragraphs:
                                if p.strip():
                                    self.documents.append({
                                        "source": file,
                                        "content": p.strip()
                                    })
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
        print(f"Loaded {len(self.documents)} paragraphs from local files.")

    def normalize_text(self, text: str) -> str:
        """Removes accents and diacritics for easier searching."""
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn').lower()

    def generate(self, query: str, age: int, education: str, tone: str) -> NarrativeResponse:
        """
        Generates a response based on keyword matching.
        """
        if not self.documents:
             self.load_data() # Try loading again just in case
             if not self.documents:
                return NarrativeResponse(
                    narrative="I currently have no historical data loaded. Please add text files to the data directory.",
                    timeline=[],
                    sources=[],
                    metadata={"info": "No data found"}
                )

        normalized_query = self.normalize_text(query)
        keywords = [self.normalize_text(k) for k in query.split() if len(k) >= 3] # simple stopword filtering
        if not keywords:
            keywords = [normalized_query]

        # Custom logic to handle "Oriki" or "Praise" queries
        is_oriki_query = "oriki" in normalized_query or "praise" in normalized_query

        # Score paragraphs
        scored_docs = []
        for doc in self.documents:
            score = 0
            content_lower = doc["content"].lower()
            content_normalized = self.normalize_text(doc["content"])
            
            # Boost if document is likely Oriki and query asks for it
            is_oriki_doc = "oriki" in doc["source"].lower() or "oriki" in content_lower[:50]
            
            if is_oriki_query and is_oriki_doc:
                score += 5 # Significant boost for intended content type
            
            # Tokenize content for fuzzy matching
            content_tokens = content_normalized.split()

            for k in keywords:
                # Exact match
                if k in content_normalized:
                    score += 2
                else:
                    # Fuzzy match check
                    # Check if 'k' is similar to any word in the content
                    matches = difflib.get_close_matches(k, content_tokens, n=1, cutoff=0.8)
                    if matches:
                        score += 1  # Moderate boost for fuzzy match
            
            # Extra boost for exact phrase match
            if normalized_query in content_normalized:
                score += 3
                
            if score > 0:
                scored_docs.append((score, doc))

        # Sort by score
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Take top 3
        top_docs = scored_docs[:3]
        
        if not top_docs:
             return NarrativeResponse(
                narrative="I searched the archives but couldn't find specific information matching your query. Try asking about 'Owu origins', 'wars', or 'culture'.",
                timeline=[],
                sources=[],
                metadata={"info": "No matches"}
            )

        # Construct Narrative
        narrative_parts = [d[1]["content"] for d in top_docs]
        narrative = "\n\n".join(narrative_parts)
        
        # Construct Timeline (Simple year extraction)
        timeline = []
        years = re.findall(r'\b(1[0-9]{3}|20[0-2][0-9])\b', narrative)
        years = sorted(list(set(years)))
        for year in years:
             # Find context for year
             for part in narrative_parts:
                 if year in part:
                     # Grab a snippet
                     snippet_idx = part.find(year)
                     snippet = part[snippet_idx:snippet_idx+50] + "..."
                     timeline.append(TimelineEvent(year=year, event=snippet))
                     break

        # Sourced
        sources = []
        seen_sources = set()
        for _, doc in top_docs:
            if doc["source"] not in seen_sources:
                 sources.append(Source(title=doc["source"], type="Local Record", confidence_score=1.0))
                 seen_sources.add(doc["source"])

        return NarrativeResponse(
            narrative=narrative,
            timeline=timeline,
            sources=sources,
            metadata={"mode": "Local Search"}
        )
