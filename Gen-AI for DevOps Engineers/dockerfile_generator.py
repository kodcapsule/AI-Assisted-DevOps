# import ollama
import click
from colorama import Fore,  init
from pyfiglet import figlet_format
import sys

from DockerfileGenerator import DockerfileGenerator
from utils import progress_bar,hosted_llm 


SUPPORTED_LANGUAGES = [
    "python", "javascript", "java", "csharp", "c++", "ruby", "go","golang",
    "typescript","c#"
]

MODEL_TYPES = ['local', 'online']



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
@click.option('--model-type', '-t',
    type=click.Choice(MODEL_TYPES, case_sensitive=False),
    prompt='Choose model type',
    default='local',
    help='Select whether to use a local or online model')
def generate_dockerfile(language, output, model_type):
    """
    Generates a Dockerfile for the specified programming language using Ollama.    
    Args:
        language (str): The programming language for which to generate the Dockerfile.    
    Returns:
        str: The generated Dockerfile content.
    """  
 
    print()
    print(Fore.GREEN + "All Configuration files are ok ✅:")
    print(f"   📝 Language: {language.title()}")
    print(f"   🤖 Model Type: {model_type.title()}")
    print(f"   📁 Output: {output}")
    print()
       

    if model_type == 'local':
        try:
            
            dockerfile_gen = DockerfileGenerator(language=language)
            print(Fore.YELLOW + "Using Local model")
            progress_bar.styled_progress_bar()
            dockerfile_gen.generate_and_save()
        except ImportError:
            print(Fore.RED + "Ollama package is not installed. Please install it using 'pip install ollama'.")
            sys.exit(1)
        except Exception as e:
                print(f"Error generating Dockerfile: {str(e)}")
                sys.exit(1)

    elif model_type == 'online':
        try:
            print(Fore.YELLOW + "Using online model. Ensure you have an internet connection.")
            progress_bar.styled_progress_bar()
            hosted_llm.generate_dockerfile(language=language, model_type='gemini-1.5-pro')
            print(Fore.GREEN + "Dockerfile generated successfully using online model!")
        except ImportError:
            print(Fore.RED + "Ollama package is not installed. Please install it using 'pip install ollama'.")
            sys.exit(1)
        except Exception as e:
                print(f"Error generating Dockerfile: {str(e)}")
                sys.exit(1)
    else:
        print(Fore.RED + "Invalid model type selected. Please choose 'local' or 'online'.")
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
     # Show custom progress bar after main function completes