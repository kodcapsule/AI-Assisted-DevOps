import os
import subprocess
import platform
from termcolor import colored

class OllamaChecker:
    """A class to check if Ollama is installed and running on the system."""
    
    def __init__(self):
        """Initialize the OllamaChecker instance."""
        self.system = platform.system()
        self.installation_status = None
        self.installation_details = None
        self.process_status = None
        self.process_details = None
        self.service_status = None
        self.service_details = None
        
    def check_installed(self):
        """Check if Ollama is installed on the system."""
        try:
            if self.system == "Windows":
                # On Windows, check for Ollama in Program Files or AppData
                paths_to_check = [
                    os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Ollama'),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Ollama')
                ]
                
                for path in paths_to_check:
                    if os.path.exists(path):
                        message = f"Your OS is {platform.system()} {platform.release()} running Python {platform.python_version()}\n"
                        self.installation_status = True
                        self.installation_details = colored(f"Ollama is  installed at: {path} \n{message}",'cyan', attrs=["bold"])
                        return self.installation_status, self.installation_details
                        
                # Try to run ollama command
                result = subprocess.run(['where', 'ollama'], capture_output=True, text=True) 
                if result.returncode == 0:
                    self.installation_status = True
                    self.installation_details = f"Ollama appears to be installed at 101: {result.stdout.strip()}"
                    return self.installation_status, self.installation_details
                
                else:
                    self.installation_status = False
                    self.installation_details = "Ollama is not installed."
                
            elif self.system in ["Linux", "Darwin"]:  # Linux or macOS
                # Check if ollama is in PATH
                result = subprocess.run(['which', 'ollama'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.installation_status = True
                    self.installation_details = f"Ollama appears to be installed at: {result.stdout.strip()}"
                    return self.installation_status, self.installation_details
                
                # Check common installation directories
                paths_to_check = [
                    '/usr/local/bin/ollama',
                    '/usr/bin/ollama',
                    '/opt/ollama/bin/ollama',
                    os.path.expanduser('~/.local/bin/ollama')
                ]
                
                if self.system == "Darwin":  # macOS specific paths
                    paths_to_check.append('/Applications/Ollama.app')
                    
                for path in paths_to_check:
                    if os.path.exists(path):
                        self.installation_status = True
                        self.installation_details = f"Ollama appears to be installed at: {path}"
                        return self.installation_status, self.installation_details
                        
                self.installation_status = False
                self.installation_details = "Ollama does not appear to be installed."
            else:
                self.installation_status = False
                self.installation_details = f"Unsupported operating system: {self.system}"
                
        except Exception as e:
            self.installation_status = False
            self.installation_details = f"Error checking Ollama installation: {str(e)}"
            
        return self.installation_status, self.installation_details

    def check_process_running(self):
        """Check if Ollama process is running."""
        try:
            if self.system == "Windows":
                # Using tasklist on Windows
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ollama.exe'], 
                                       capture_output=True, text=True)
                self.process_status = "ollama.exe" in result.stdout
                self.process_details = result.stdout.strip()
                
            elif self.system in ["Linux", "Darwin"]:
                # Using ps on Linux/macOS
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                self.process_status = "ollama" in result.stdout
                self.process_details = "Process found" if "ollama" in result.stdout else "Process not found"
                
            else:
                self.process_status = False
                self.process_details = f"Unsupported operating system: {self.system}"
                
        except Exception as e:
            self.process_status = False
            self.process_details = f"Error checking if Ollama is running: {str(e)}"
            
        return self.process_status, self.process_details

    def check_service_running(self):
        """Check if Ollama service is running by attempting to connect to its API."""
        try:
            import requests
            # Ollama typically runs on port 11434
            response = requests.get("http://localhost:11434/api/version", timeout=3)
            
            if response.status_code == 200:
                self.service_status = True
                self.service_details = f"Ollama API is responsive. Version: {response.json().get('version', 'unknown')}"
            else:
                self.service_status = False
                self.service_details = f"Ollama API returned status code: {response.status_code}"
                
        except ImportError:
            self.service_status = False
            self.service_details = "Cannot check Ollama API: requests module not installed"
        except requests.exceptions.ConnectionError:
            self.service_status = False
            self.service_details = "Cannot connect to Ollama API. Service may not be running."
        except Exception as e:
            self.service_status = False
            self.service_details = f"Error checking Ollama service: {str(e)}"
            
        return self.service_status, self.service_details
    
    def check_all(self):
        """Perform all checks and return a dictionary with results."""
        self.check_installed()
        self.check_process_running()
        self.check_service_running()
        
        results = {
            "installation": {
                "status": self.installation_status,
                "details": self.installation_details
            },
            "process": {
                "status": self.process_status,
                "details": self.process_details
            },
            "service": {
                "status": self.service_status,
                "details": self.service_details
            },
            "overall": self.is_operational()
        }
        
        return results
    
    def is_operational(self):
        """Determine if Ollama is fully operational based on all checks."""
        if self.installation_status is None:
            self.check_installed()
            
        if self.process_status is None:
            self.check_process_running()
            
        if self.service_status is None:
            self.check_service_running()
            
        return self.installation_status and (self.process_status or self.service_status)
    
    def print_status(self):
        """Print the status of Ollama in a readable format."""
        if any(status is None for status in [self.installation_status, self.process_status, self.service_status]):
            self.check_all()
            
        print("Ollama Status Check Results:")
        print("-" * 30)
        
        print(f"Installation: {'Installed' if self.installation_status else 'Not installed'}")
        print(f"  Details: {self.installation_details}")
        
        print(f"Process: {'Running' if self.process_status else 'Not running'}")
        print(f"  Details: {self.process_details}")
        
        print(f"Service: {'Running' if self.service_status else 'Not running'}")
        print(f"  Details: {self.service_details}")
        
        print("-" * 30)
        if self.is_operational():
            print("OVERALL: Ollama appears to be installed and running.")
        elif self.installation_status:
            print("OVERALL: Ollama is installed but does not appear to be running.")
        else:
            print("OVERALL: Ollama does not appear to be installed on this system.")


#   