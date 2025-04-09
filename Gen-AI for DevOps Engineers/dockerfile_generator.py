import ollama
from termcolor import colored
import sys, os, platform, subprocess
import re

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


def check_ollama_installed():
 
    try: 
        system = platform.system()
        
        if system == "Windows":
            # On Windows, check for Ollama in Program Files or AppData
            paths_to_check = [
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Ollama'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Ollama')
            ]
            
            for path in paths_to_check:
                if os.path.exists(path):
                    return True,f"✅ Ollama appears to be installed at: {path}"
                  
                    
            # Try to run ollama command
            result = subprocess.run(['where', 'ollama'], capture_output=True, text=True)
            if result.returncode == 0:
                return True, f"Ollama appears to be installed at: {result.stdout.strip()}"
            
            return False, "❌ Ollama does not appear to be installed."
        
    except Exception as e:
        return False, f"Error checking Ollama installation: {str(e)}"








def validate_language(language):
    """Validate if the provided language is a real programming language."""
    input_language = language.lower().strip()
    if not input_language:
            print(colored(" 🛑 ERROR: Programming language cannot be empty", 'red',attrs=["bold"]))            
            sys.exit(1)
    elif input_language in COMMON_LANGUAGES:
        print (f"'{input_language}' is a common programming language.")
        return input_language
    else:
        print(colored(f"⚠️  WARNING: '{input_language}' is not recognized as a common programming language. Input may be incorrect.", 'yellow',attrs=["bold"]))                
        sys.exit(1)
   

def generate_dockerfile(language):
    """Generate a Dockerfile for the specified language using Ollama."""
    try:
                       
        print(f"Generating Dockerfile for {language}...")

  
 #===================================================================  
    #     # Call Ollama API to generate Dockerfile
    #     response = ollama.chat(
    #         model='llama3.1:8b', 
    #         messages=[{'role': 'user', 'content': PROMPT.format(language=language)}]
    #     )
        
    #     # Extract content from response
    #     dockerfile_content = response['message']['content']
        
    #     # Basic verification that we got a Dockerfile
    #     if not dockerfile_content or "FROM" not in dockerfile_content:
    #         raise ValueError("Generated content does not appear to be a valid Dockerfile")
            
    #     return dockerfile_content
        
    # except ImportError:
    #     print("Error: The ollama package is not installed. Install it with 'pip install ollama'")
    #     sys.exit(1)
    # except ConnectionError:
    #     print("Error: Could not connect to Ollama service. Make sure it's running.")
    #     sys.exit(1)
    except Exception as e:
        print(f"Error generating Dockerfile: {str(e)}")
        sys.exit(1)







def main():
    try:
        # Get language input with validation
        language = input("Enter the programming language: ").strip()
        valid_language = validate_language(language)
            
        # check if Ollama is installed locally and running

       # check if ollama is installed on the OS and the service is running

        try:
            ollama.list_models()
        except ImportError:
            print(colored("ERROR: The ollama package is not installed. Install it with 'pip install ollama'", 'red', attrs=["bold"]))
            sys.exit(1)
        except ConnectionError:
            print(colored("ERROR: Could not connect to Ollama service. Make sure it's running.", 'red', attrs=["bold"]))
            sys.exit(1)
       
        
        # Generate the Dockerfile
        dockerfile = generate_dockerfile(valid_language)
        
        # Display the result
        print("\nGenerated Dockerfile:\n")
        print(dockerfile)
        
        # Optionally save to file
        save_option = input("\nWould you like to save this Dockerfile? (y/n): ").lower()
        if save_option == 'y':
            with open("Dockerfile", "w") as f:
                f.write(dockerfile)
            print(colored("Dockerfile saved successfully!", 'green', attrs=["bold"]))
        else:
            print(colored("Dockerfile not saved.", 'yellow', attrs=["bold"]))   
            
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)




def greeting():
    """Display a greeting message."""


    print(colored("======== Welcome to the Dockerfile Generator! =====\nThis tool generates Dockerfiles for various programming languages.\nPlease ensure you " \
    "have Ollama installed and running.", 'cyan', attrs=["bold"]))

    print(colored(f"Your OS is {platform.system()} {platform.release()} running Python {platform.python_version()} installed", 'cyan', attrs=["bold"]))

    # Check if Ollama is installed and running
    ollama_installed, message = check_ollama_installed()
    if ollama_installed:
        print(colored(message, 'green', attrs=["bold"]))
    else:
        print(colored(message, 'red', attrs=["bold"]))





if __name__ == '__main__':

    greeting()
    
    main()