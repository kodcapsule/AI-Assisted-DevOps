import sys
import ollama
from OllamaChecker import OllamaChecker

PROMPT = """
        ONLY Generate an ideal Dockerfile for {language} with best practices. Do not provide any description
        Include:
        - Base image
        - Installing dependencies
        - Setting working directory
        - Adding source code
        - Running the application
        - Exposing necessary ports
        - Using multi-stage builds if applicable
        - Ensure the Dockerfile is production-ready and follows Docker best practices
        """

class DockerfileGenerator:
    """A class to generate Dockerfiles for different programming languages using Ollama."""
    
    def __init__(self, model='llama3.1:8b', language ='python',prompt_template=PROMPT ):
        """Initialize the DockerfileGenerator with a specified model.
        
        Args:
            model (str): The Ollama model to use for generation. Default is 'llama3.1:8b'.
            language (str): The programming language for which to generate a Dockerfile. Default is 'python'.
            
        """
        self.language = language
        self.model = model
        self.prompt_template = prompt_template
    
    def set_prompt_template(self, template):
        """Set a custom prompt template for Dockerfile generation.
        
        Args:
            template (str): The prompt template with {language} placeholder.
        """
        self.prompt_template = template
    


    def generate(self, language):
        """Generate a Dockerfile for the specified language using Ollama.
        
        Args:
            language (str): The programming language for which to generate a Dockerfile.
            
        Returns:
            str: The generated Dockerfile content.
            
        Raises:
            ImportError: If the ollama package is not installed.
            ConnectionError: If unable to connect to Ollama service.
            ValueError: If the generated content is not a valid Dockerfile.
            Exception: For any other errors.
        """
        ollama_checker = OllamaChecker()
        try:

            # Check if Ollama is installed and running
            if not ollama_checker.check_installed():
                print("Ollama is not installed. Please install it first.")
                sys.exit(1)
            elif not ollama_checker.check_process_running():
                print("Ollama process is not running. Please start it first.")
                sys.exit(1)
            elif not ollama_checker.check_service_running():
                print("Ollama service is not running. Please ensure it is started.")
                sys.exit(1)
            else:
                print("Ollama is installed and running. Proceeding with Dockerfile generation...")
            
         
         
            
            



            # Call Ollama API to generate Dockerfile
            try:
                # print(f"Generating Dockerfile for {language}...")
                response = ollama.chat(
                    model=self.model,
                    messages=[{'role': 'user', 'content': self.prompt_template.format(language=language)}]
                )
                
                # Extract content from response
                dockerfile_content = response['message']['content']
                
                # Basic verification that we got a Dockerfile
                if not dockerfile_content or "FROM" not in dockerfile_content:
                    raise ValueError("Generated content does not appear to be a valid Dockerfile")
                
                return dockerfile_content
                
            except ImportError:
                print("Error: The ollama package is not installed. Install it with 'pip install ollama'")
                sys.exit(1)
            except ConnectionError:
                print("Error: Could not connect to Ollama service. Make sure it's running.")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error generating Dockerfile: {str(e)}")
            sys.exit(1)
    
    def save_to_file(self, content, filepath="Dockerfile"):
        """Save the generated Dockerfile content to a file.
        
        Args:
            content (str): The Dockerfile content to save.
            filepath (str): The filepath to save the Dockerfile to. Default is "Dockerfile".
            
        Returns:
            bool: True if the file was saved successfully, False otherwise.
        """
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Dockerfile saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving Dockerfile: {str(e)}")
            return False
    
    def generate_and_save(self, filepath="Dockerfile"):
        """Generate a Dockerfile for the specified language and save it to a file.
        
        Args:
            language (str): The programming language for which to generate a Dockerfile.
            filepath (str): The filepath to save the Dockerfile to. Default is "Dockerfile".
            
        Returns:
            bool: True if the Dockerfile was generated and saved successfully, False otherwise.
        """
        try:
            content = self.generate(self.language)
            return self.save_to_file(content, filepath)
        except Exception as e:
            print(f"Error generating and saving Dockerfile: {str(e)}")
            return False

