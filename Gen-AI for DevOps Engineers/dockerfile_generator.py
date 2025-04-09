import ollama
from termcolor import colored
import sys, os, platform, subprocess
import OllamaChecker
import DockerfileGenerator
PROMPT = """
ONLY Generate an ideal Dockerfile for {language} with best practices. Do not provide any description
Include:
- Base image
- Installing dependencies
- Setting working directory
- Adding source code
- Running the application
"""

# List of common programming languages to validate input against
COMMON_LANGUAGES = [
    'python', 'javascript', 'typescript', 'node', 'nodejs', 'java', 'go', 'golang', 
    'ruby', 'php', 'csharp', 'c#', '.net', 'rust', 'c', 'c++', 'swift', 'kotlin', 
    'scala', 'elixir', 'perl', 'r', 'dart', 'flutter', 'haskell', 'clojure'
]


ollama_checker = OllamaChecker.OllamaChecker()







def validate_language(language):
    """Validate if the provided language is a real programming language."""
    input_language = language.lower().strip()
    if not input_language:
                   
            return 'python'  # Default to Python if no input is provided
    elif input_language in COMMON_LANGUAGES:
        print (f"'{input_language}' is a common programming language.")
        return input_language
    else:
        print(colored(f"⚠️  WARNING: '{input_language}' is not recognized as a common programming language. Input may be incorrect.", 'yellow',attrs=["bold"]))                
        sys.exit(1)



def main():
    try:
        # Get language input with validation
        dockerfile_generator = DockerfileGenerator.DockerfileGenerator()
        language = input("Enter the programming language , Default is Python: ").strip()
        valid_language = validate_language(language)          
        
        # Generate the Dockerfile
        dockerfile = dockerfile_generator.generate(valid_language)
        
        # Display the result
        print("\nGenerated Dockerfile:\n")
        print(dockerfile)
 
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)




def greeting():
    """Display a greeting message."""
    print(colored("\n======== Welcome to the Dockerfile Generator! =====\nThis tool generates Dockerfiles for various programming languages.\nPlease ensure you " \
    "have Ollama installed and running.\n", 'cyan', attrs=["bold"]))

    # Check if Ollama is installed and running
    is_installed, installation_details = ollama_checker.check_installed()        
    if is_installed:        
        print(installation_details)
    else:
        print(colored(installation_details, 'red', attrs=["bold"]))





if __name__ == '__main__':

    greeting()    
    main() 