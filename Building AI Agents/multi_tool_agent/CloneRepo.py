from typing import Dict, List, Any, Optional
import os
import subprocess
import tempfile
import logging
import re
from pathlib import Path

# from google.ai.adk.agents import LlmAgent
# from google.ai.adk.tools import Tool, ToolRegistry
# from google.ai.adk.tools.responses import ContentResponse, ErrorResponse


from termcolor import colored

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("REPO CLONE AGENT")


# validate git installation
def validate_git_installation() -> bool:
    """Check if Git is installed on the system."""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
        logger.info(colored(f"\nGit is installed: {result.stdout.strip()}\n", 'green', attrs=["bold"]))        
        return True
    except subprocess.CalledProcessError:
        logger.error("\nGit is not installed or not found in PATH.\n")
        return False
    



def validate_repo_url(repo_url: str) -> bool:
    """Validate if the provided URL is a valid Git repository URL."""
    # Basic pattern matching for common git repository URLs
    git_url_pattern = r'^(https?://|git@)(github\.com|gitlab\.com|bitbucket\.org|dev\.azure\.com)(/|:).+(/|\.git)?$'
    return bool(re.match(git_url_pattern, repo_url))


# ======================================  CLONE REPOSITORY   =====================================================

def clone_repository(repo_url: str, target_dir: Optional[str] = None) -> Dict[str, Any]:
    """Clone a Git repository from the provided URL."""
    logger.info(f"Attempting to clone repository from: {repo_url}")
    
    if not validate_repo_url(repo_url):
        return {
            "success": False,
            "error": "Invalid repository URL. Please provide a valid GitHub, GitLab, Bitbucket, or Azure DevOps URL."
        }
    
    # Use provided target directory or create a temporary one
    if not target_dir:
        target_dir = tempfile.mkdtemp(prefix="repo_clone_")
    
    target_path = Path(target_dir)
    if not target_path.exists():
        target_path.mkdir(parents=True)
    
    try:
        # Run git clone command
        result = subprocess.run(
            ["git", "clone", repo_url, target_dir],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Git clone failed: {result.stderr}",
                "command_output": result.stderr
            }
        
        # Get repository metadata
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        
        # Count files and directories
        file_count = sum(1 for _ in Path(target_dir).glob('**/*') if _.is_file())
        dir_count = sum(1 for _ in Path(target_dir).glob('**/*') if _.is_dir())
        
        return {
            "success": True,
            "repo_url": repo_url,
            "repo_name": repo_name,
            "clone_path": target_dir,
            "file_count": file_count,
            "directory_count": dir_count,
            "command_output": result.stdout
        }
        
    except Exception as e:
        logger.error(f"Failed to clone repository: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to clone repository: {str(e)}"
        }


# ======================================  LIST REPOSITORY CONTENTS   =====================================================

# def list_repository_contents(repo_path: str, max_files: int = 20) -> Dict[str, Any]:
#     """List the contents of a cloned repository."""
#     try:
#         repo_dir = Path(repo_path)
#         if not repo_dir.exists() or not repo_dir.is_dir():
#             return {
#                 "success": False,
#                 "error": f"Repository path '{repo_path}' does not exist or is not a directory."
#             }
        
#         # Get all files recursively
#         all_files = list(repo_dir.glob('**/*'))
        
#         # Filter out directories and hidden files
#         files = [str(f.relative_to(repo_dir)) for f in all_files 
#                 if f.is_file() and not any(part.startswith('.') for part in f.parts)]
        
#         # Get directories (excluding hidden directories)
#         dirs = [str(d.relative_to(repo_dir)) for d in all_files 
#                if d.is_dir() and not any(part.startswith('.') for part in d.parts)]
        
#         # Find specific file types
#         file_types = {}
#         for file in files:
#             ext = Path(file).suffix.lower()
#             if ext:
#                 if ext not in file_types:
#                     file_types[ext] = 0
#                 file_types[ext] += 1
        
#         # Check for project type indicators
#         project_indicators = {
#             "Python": any(f.endswith(('.py', 'requirements.txt', 'setup.py')) for f in files),
#             "JavaScript/Node.js": any(f.endswith(('package.json', '.js', '.jsx', '.ts', '.tsx')) for f in files),
#             "Java": any(f.endswith(('.java', 'pom.xml', 'build.gradle')) for f in files),
#             "Go": any(f.endswith(('.go', 'go.mod')) for f in files),
#             "Ruby": any(f.endswith(('.rb', 'Gemfile')) for f in files),
#             "C#/.NET": any(f.endswith(('.cs', '.csproj', '.sln')) for f in files),
#             "PHP": any(f.endswith('.php') for f in files)
#         }
        
#         detected_project_types = [lang for lang, detected in project_indicators.items() if detected]
        
#         return {
#             "success": True,
#             "total_files": len(files),
#             "total_directories": len(dirs),
#             "file_types": file_types,
#             "detected_project_types": detected_project_types,
#             "files": files[:max_files],  # Limit the number of files to avoid large responses
#             "truncated_file_list": len(files) > max_files
#         }
    
#     except Exception as e:
#         logger.error(f"Failed to list repository contents: {str(e)}")
#         return {
#             "success": False,
#             "error": f"Failed to list repository contents: {str(e)}"
#         }


# ===============================================  TOOLS   =====================================================


# # Define tool for cloning repositories
# class CloneRepositoryTool(Tool):
#     def __call__(self, repo_url: str, target_dir: Optional[str] = None) -> ContentResponse | ErrorResponse:
#         """Clone a public Git repository from URL.
        
#         Args:
#             repo_url: URL of the Git repository to clone (e.g., https://github.com/username/repo)
#             target_dir: Optional directory where the repository should be cloned
            
#         Returns:
#             Information about the cloned repository or error details
#         """
#         result = clone_repository(repo_url, target_dir)
        
#         if result["success"]:
#             return ContentResponse(content=result)
#         else:
#             return ErrorResponse(error=result["error"])

# # Define tool for listing repository contents
# class ListRepositoryContentsTool(Tool):
#     def __call__(self, repo_path: str, max_files: int = 20) -> ContentResponse | ErrorResponse:
#         """List contents of a cloned repository.
        
#         Args:
#             repo_path: Path to the cloned repository
#             max_files: Maximum number of files to list (default: 20)
            
#         Returns:
#             Information about repository contents or error details
#         """
#         result = list_repository_contents(repo_path, max_files)
        
#         if result["success"]:
#             return ContentResponse(content=result)
#         else:
#             return ErrorResponse(error=result["error"])


# ===============================  CLONEREPO AGENT   ==========================================
# # Create the repository clone agent
# def create_repo_clone_agent() -> LlmAgent:
#     """Create and configure the repository clone agent."""
    
#     # Create tool registry and register tools
#     tools = ToolRegistry()
#     tools.register(CloneRepositoryTool())
#     tools.register(ListRepositoryContentsTool())
    
#     # Create the agent
#     repo_clone_agent = LlmAgent(
#         model="gemini-2.0-flash-exp",
#         name="repo_clone_agent",
#         description="Clones code repositories from public URLs and analyzes their contents.",
#         instruction="""You are an agent that helps users clone and analyze public code repositories.

# When a user provides a repository URL or asks to clone a repository:
# 1. Validate if the URL is a valid Git repository URL (GitHub, GitLab, Bitbucket, Azure DevOps)
# 2. Use the `CloneRepositoryTool` to clone the repository
# 3. Provide information about the cloned repository including location and basic stats
# 4. Offer to analyze the repository contents using `ListRepositoryContentsTool`

# When analyzing repository contents:
# 1. Identify the programming languages and frameworks used
# 2. Highlight key project files (e.g., README, configuration files)
# 3. Provide an overview of the repository structure

# Example Query: "Clone this repository: https://github.com/username/repo"
# Example Response: "I've successfully cloned the repository from https://github.com/username/repo. 
# The repository contains 85 files across 12 directories and appears to be a Python project.
# Would you like me to analyze the repository contents in more detail?"

# Always be security-conscious and only clone repositories from trusted sources.
# """,
#         tools=tools
#     )
    
#     return repo_clone_agent

# Example usage
if __name__ == "__main__":
    validate_git_installation()
    # validate_repo_url(https://github.com/google/adk-python?tab=readme-ov-file)
    
    # agent = create_repo_clone_agent()
    # In a real implementation, you would serve this agent
    # agent.serve()