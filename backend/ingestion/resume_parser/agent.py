import os
import yaml
import google.generativeai as genai
from pydantic import ValidationError
from pathlib import Path
from models.schemas import CandidateProfile

def _load_prompt() -> str:
    """Loads the system prompt for the resume parser from the local YAML file."""
    prompt_path = Path(__file__).parent / "prompts.yaml"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found at {prompt_path}")
        
    with open(prompt_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        return data.get("system_prompt", "You are an expert resume parser. Extract candidate details accurately.")

def parse_resume(raw_resume_text: str) -> CandidateProfile:
    """
    Parses unstructured resume text into a structured CandidateProfile using Gemini 1.5 Flash.
    
    Args:
        raw_resume_text (str): The raw text extracted from a resume PDF.
        
    Returns:
        CandidateProfile: A strictly validated Pydantic model containing the parsed data.
    """
    # Ensure API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please configure it.")
        
    genai.configure(api_key=api_key)
    
    system_instruction = _load_prompt()
    
    # Initialize the model with system instructions
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_instruction
    )
    
    # Force Gemini to return JSON that matches our Pydantic model
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=CandidateProfile
    )
    
    try:
        response = model.generate_content(
            raw_resume_text,
            generation_config=generation_config
        )
        
        # Validate and return the parsed JSON as our Pydantic model
        return CandidateProfile.model_validate_json(response.text)
        
    except ValidationError as e:
        # In a production environment, we would log this to an observability platform
        raise RuntimeError(f"Failed to validate parsed resume data against schema: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred during resume parsing: {e}")