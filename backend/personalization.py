from typing import Dict, Any

def adjust_prompt(query: str, age: int, education: str, tone: str) -> str:
    """
    Constructs a sophisticated system prompt based on user demographics and preferences.
    """
    
    # 1. Age-Based Adaptation
    if age < 12:
        complexity = "Simple language, short sentences, focus on exciting stories."
        perspective = "Like a wise elder telling a bedtime story."
    elif age < 18:
        complexity = "Moderate complexity, relatable analogies, focus on cause and effect."
        perspective = "Engaging history teacher."
    else:
        complexity = "Full complexity, nuanced vocabulary."
        perspective = "Objective historian or cultural custodian."

    # 2. Education/Depth Level
    if education == "Academic":
        depth_instruction = "Provide a rigorous academic analysis. Cite specific sources, discuss historiographical debates if any, and use formal terminology."
    elif education == "General":
        depth_instruction = "Provide a balanced overview suitable for a general audience. Explain context clearly."
    else: # Child/Simplified
        depth_instruction = "Focus on the main characters and events. Avoid jargon."

    # 3. Tone/Style
    if tone == "Storyteller":
        style_instruction = "Weave the facts into a compelling narrative. Use evocative language to set the scene."
    elif tone == "Formal":
        style_instruction = "Maintain a strictly formal and objective tone."
    else: # Neutral
        style_instruction = "Be informative and direct."

    # Construct the System Instruction
    system_instruction = f"""
    You are an expert historian of the Owu people. 
    Target Audience: {age} years old.
    Persona: {perspective}
    Language Style: {complexity}
    
    Task: Answer the user's query about Owu history.
    
    Directives:
    1. {depth_instruction}
    2. {style_instruction}
    3. ALWAYS verify your facts against the provided context. If the context does not contain the answer, admit it.
    4. Culturally, treat the Olowu and major figures with deep respect.
    """

    return system_instruction
