import ollama
import sys
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

def is_valid_language(language):
    """Validate if the provided language is a real programming language."""
    language = language.lower().strip()
    return language in COMMON_LANGUAGES

def generate_dockerfile(language):
    """Generate a Dockerfile for the specified language using Ollama."""
    try:
        # Check if language is valid
        if not language or not isinstance(language, str):
            raise ValueError("Language must be a non-empty string")
            
        # Check if language is a known programming language
        if not is_valid_language(language):
            print(f"Warning: '{language}' is not recognized as a common programming language. Continuing anyway...")
            
        # Call Ollama API to generate Dockerfile
        response = ollama.chat(
            model='llama3.1:8b', 
            messages=[{'role': 'user', 'content': PROMPT.format(language=language)}]
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

def main():
    try:
        # Get language input with validation
        language = input("Enter the programming language: ").strip()
        
        if not language:
            print("Error: Programming language cannot be empty")
            sys.exit(1)
            
        # Generate the Dockerfile
        dockerfile = generate_dockerfile(language)
        
        # Display the result
        print("\nGenerated Dockerfile:\n")
        print(dockerfile)
        
        # Optionally save to file
        save_option = input("\nWould you like to save this Dockerfile? (y/n): ").lower()
        if save_option == 'y':
            with open("Dockerfile", "w") as f:
                f.write(dockerfile)
            print("Dockerfile saved successfully!")
            
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()