from pydantic import BaseModel, Field
from typing import List, Optional

class TimelineEvent(BaseModel):
    year: str = Field(..., description="The year or era of the event")
    event: str = Field(..., description="Description of the historical event")

class Source(BaseModel):
    title: str = Field(..., description="Title of the document or source")
    type: str = Field(..., description="Type of source (e.g., 'Oral Tradition', 'Academic Paper')")
    confidence_score: float = Field(..., description="Relevance score (0-1.0)")

class NarrativeResponse(BaseModel):
    narrative: str = Field(..., description="The generated historical narrative")
    timeline: List[TimelineEvent] = Field(default_factory=list, description="Key events extracted from the narrative")
    sources: List[Source] = Field(default_factory=list, description="List of sources used")
    metadata: dict = Field(default_factory=dict, description="Additional metadata like tone, age group used")

class NarrativeRequest(BaseModel):
    query: str
    user_age: int = 25
    education_level: str = "General"  # 'General', 'Academic', 'Child'
    tone: str = "Neutral" # 'Neutral', 'Storyteller', 'Formal'
