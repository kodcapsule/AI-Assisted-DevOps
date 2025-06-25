import google.generativeai as genai
import os

from dotenv import load_dotenv

load_dotenv()

def generate_dockerfile(language="python", model_type="gemini-1.5-pro"):
    """
    Generate a Dockerfile for the specified programming language using a hosted LLM.

    Args:
        language (str): The programming language for which to generate the Dockerfile.
        model_type (str): The type of model to use ('local' or 'online').
        output (str): The output directory where the Dockerfile will be saved.

    Returns:
        str: The generated Dockerfile content.
    """
    
    # Set up the Google Generative AI API key
   
    
# Configure the Gemini model
    genai.configure(api_key=os.getenv("API_KEY"))
    model = genai.GenerativeModel(model_name=model_type)

    PROMPT = """
    Generate an ideal Dockerfile for {language} with best practices. Just share the dockerfile without any explanation between two lines to make copying dockerfile easy.
    Include:
    - Base image
    - Installing dependencies
    - Setting working directory
    - Adding source code
    - Running the application
    """
    response = model.generate_content(PROMPT.format(language=language))
    return response.text