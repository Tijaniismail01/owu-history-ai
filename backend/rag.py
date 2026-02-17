import os
import json
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.output_parsers import PydanticOutputParser
from pydantic import ValidationError

from .schemas import NarrativeResponse, TimelineEvent, Source
from .personalization import adjust_prompt

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# Initialize Global Components
embeddings = OpenAIEmbeddings()

def get_vectorstore():
    if not os.path.exists(DB_DIR):
        # Return empty or handle gracefully if no DB yet
        return None
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

def get_qa_chain():
    """
    Returns a function that takes a query and user params, 
    and returns a structured NarrativeResponse.
    """
    vectorstore = get_vectorstore()
    if not vectorstore:
        return None

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    def process_query(query: str, age: int, education: str, tone: str) -> NarrativeResponse:
        # 1. Generate Personalized Instruction
        system_instruction = adjust_prompt(query, age, education, tone)
        
        # 2. Construct Prompt
        # We ask for JSON output explicitly in the prompt to ensure parsing check.
        # Although PydanticOutputParser is good, for complex narrative + timeline, 
        # a two-step or well-prompted single step is often more robust.
        
        template = """
        {system_instruction}
        
        Context from Owu Archives:
        {context}
        
        User Query: {question}
        
        OUTPUT FORMAT INSTRUCTIONS:
        You must output a valid JSON object matching this structure:
        {{
            "narrative": "The historical narrative text...",
            "timeline": [
                {{"year": "1821", "event": "Owu War begins"}},
                ...
            ],
            "sources": [
                {{"title": "Oral Tradition", "type": "Oral", "confidence_score": 0.9}},
                ...
            ]
        }}
        
        Ensure the 'narrative' field contains the full response.
        The 'sources' field should list the documents you used from the context.
        If you don't know the answer, set 'narrative' to "I could not find information on that in the archives."
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"],
            partial_variables={"system_instruction": system_instruction}
        )
        
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        
        # 3. Execute Chain
        result = chain({"query": query})
        raw_output = result["result"]
        source_docs = result["source_documents"]
        
        # 4. Parse Output
        try:
            # Clean up potential markdown code blocks
            json_str = raw_output.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            data = json.loads(json_str)
            
            # Enrich sources from actual retrieved docs if the LLM didn't do a perfect job
            # or to ensure accuracy.
            # For this implementation, we'll merge them.
            if not data.get("sources"):
                data["sources"] = []
                for doc in source_docs:
                    data["sources"].append({
                        "title": doc.metadata.get("source", "Unknown"),
                        "type": doc.metadata.get("type", "General"),
                        "confidence_score": 0.85 # Placeholder confidence
                    })
            
            return NarrativeResponse(**data)
            
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Parsing Error: {e}")
            # Fallback for parsing failures
            return NarrativeResponse(
                narrative=raw_output, # Return raw text if JSON fails
                timeline=[],
                sources=[Source(title="System", type="Error", confidence_score=0.0)],
                metadata={"error": "Output parsing failed"}
            )

    return process_query
