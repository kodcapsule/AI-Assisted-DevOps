# import ollama
import click
from colorama import Fore,  init
from pyfiglet import figlet_format
import sys

from DockerfileGenerator import DockerfileGenerator


SUPPORTED_LANGUAGES = [
    "python", "javascript", "java", "csharp", "c++", "ruby", "go","golang"
    "typescript","c#"
]




@click.command()
@click.option('--language', '-l',
    type=click.Choice(SUPPORTED_LANGUAGES, case_sensitive=False),
    prompt='Select a programming language',
    help='Programming language for your Dockerfile',
    default='python'
)
@click.option('--output', '-o',
    default='Dockerfile',
    help='Output file path (defaults to the current directory Dockerfile)'   
)
def generate_dockerfile(language, output):
    """
    Generates a Dockerfile for the specified programming language using Ollama.    
    Args:
        language (str): The programming language for which to generate the Dockerfile.    
    Returns:
        str: The generated Dockerfile content.
    """
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
    prompt = PROMPT.format(language=language.lower())
    try:
        print(Fore.GREEN + "All Configuration files are ok ✅:")
        print(f"   📝 Language: {language.title()}")
        print(f"   📁 Output: {output}")
        print()
       
        print(Fore.YELLOW + f"Generating Dockerfile for {language}...")
        dockerfile_gen = DockerfileGenerator(language=language,prompt_template=prompt)
        dockerfile_gen.generate_and_save()
        print(prompt)
        
    
    except Exception as e:
        print(f"Error generating Dockerfile: {str(e)}")
        sys.exit(1)

def main():
    greeting()  
    try:
       
        docker_file = generate_dockerfile()  # Generate the Dockerfile
        print(Fore.GREEN + f"\nGenerating Dockerfile for: {docker_file}\n")         
        
 
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)



def greeting():
       try:
        init(autoreset=True)       
        title = figlet_format("Dockerfile Generator", font="small",width=200)   
        print(Fore.CYAN + "=" * 60)
        print(Fore.BLUE + title)
        print(Fore.CYAN + "=" * 60)
        print(Fore.GREEN + "🐳 Welcome to the Dockerfile Generator! 🐳")
        print(Fore.WHITE + "This tool will help you generate Dockerfiles for various programming languages with ease")
        print(Fore.CYAN + "=" * 60)
        print()
       except Exception as e:
        print(f"Error during greeting: {str(e)}")
        sys.exit(1)
 
if __name__ == '__main__':
      
    main() 