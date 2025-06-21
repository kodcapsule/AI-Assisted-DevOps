import re
import urllib.parse
from typing import Tuple, Dict, Optional, List
import requests
from requests.exceptions import RequestException
import subprocess
import logging

class RepositoryValidator:
    """
    A class for validating and extracting information from Git repository URLs.
    
    This class provides functionality to validate repository URLs across various
    protocols (HTTP, HTTPS, SSH, Git) and providers (GitHub, GitLab, etc.).
    It can also verify repository existence and extract metadata.
    """
    
    def __init__(self, log_level=logging.INFO):
        """
        Initialize the repository validator.
        
        Args:
            log_level: The logging level to use
        """
        # Set up logging
        self.logger = logging.getLogger("repo_validator")
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Known Git hosting providers and their URL patterns
        self.provider_patterns = {
            "github.com": r'^https?://github\.com/[^/]+/[^/]+(/.*)?$',
            "gitlab.com": r'^https?://gitlab\.com/[^/]+/[^/]+(/.*)?$',
            "bitbucket.org": r'^https?://bitbucket\.org/[^/]+/[^/]+(/.*)?$',
            "dev.azure.com": r'^https?://dev\.azure\.com/[^/]+/[^/]+(/.*)?$',
            "source.developers.google.com": r'^https?://source\.developers\.google\.com/p/[^/]+/r/[^/]+(/.*)?$',
            "codeberg.org": r'^https?://codeberg\.org/[^/]+/[^/]+(/.*)?$',
            "gitea.com": r'^https?://gitea\.com/[^/]+/[^/]+(/.*)?$',
            "sourceforge.net": r'^https?://git\.sourceforge\.net/gitroot/[^/]+/[^/]+(/.*)?$',
        }
        
        # Mapping of hostnames to provider names
        self.provider_map = {
            "github.com": "GitHub",
            "gitlab.com": "GitLab",
            "bitbucket.org": "Bitbucket",
            "dev.azure.com": "Azure DevOps",
            "source.developers.google.com": "Google Cloud Source",
            "codeberg.org": "Codeberg",
            "gitea.com": "Gitea"
        }
        
        # Providers that support API access
        self.api_supported_providers = ["GitHub", "GitLab", "Bitbucket"]
    
    def validate_repo_url(self, repo_url: str, verify_existence: bool = False) -> Tuple[bool, Dict]:
        """
        Validate if the provided URL is a valid Git repository URL.
        
        Args:
            repo_url: The repository URL to validate
            verify_existence: If True, will make requests to verify the repository exists
            
        Returns:
            Tuple of (is_valid, details_dict)
        """
        # Normalize the URL first
        normalized_url = repo_url.strip()
        
        # Dictionary to hold validation details
        details = {
            "original_url": repo_url,
            "normalized_url": normalized_url,
            "validation_steps": [],
            "provider": None,
            "url_type": None,
            "username": None,
            "repo_name": None,
            "warnings": []
        }
        
        # Check for basic URL format first
        basic_check = self._check_basic_format(normalized_url)
        details["validation_steps"].append({"step": "basic_format", "passed": basic_check[0], "message": basic_check[1]})
        
        if not basic_check[0]:
            return False, details
        
        # Check URL structure according to protocol type
        if normalized_url.startswith(('http://', 'https://')):
            details["url_type"] = "http"
            structure_check = self._check_http_url_structure(normalized_url)
        elif normalized_url.startswith('git@'):
            details["url_type"] = "ssh"
            structure_check = self._check_ssh_url_structure(normalized_url)
        elif normalized_url.startswith('git://'):
            details["url_type"] = "git"
            structure_check = self._check_git_protocol_structure(normalized_url)
        else:
            structure_check = (False, "URL doesn't start with a recognized Git protocol")
        
        details["validation_steps"].append({"step": "structure", "passed": structure_check[0], "message": structure_check[1]})
        
        if not structure_check[0]:
            return False, details
        
        # Extract provider, username, and repository
        provider_info = self._extract_provider_info(normalized_url, details["url_type"])
        
        if not provider_info[0]:
            details["validation_steps"].append({"step": "provider_extraction", "passed": False, "message": provider_info[1]})
            return False, details
        
        details.update(provider_info[1])
        details["validation_steps"].append({"step": "provider_extraction", "passed": True, "message": f"Successfully identified as {details['provider']} repository"})
        
        # Add warnings for insecure protocols
        if normalized_url.startswith('http://'):
            details["warnings"].append("Using insecure HTTP protocol instead of HTTPS")
        
        # Verify repository existence if requested
        if verify_existence:
            existence_check = self._verify_repository_existence(normalized_url, details)
            details["validation_steps"].append({"step": "existence", "passed": existence_check[0], "message": existence_check[1]})
            
            if not existence_check[0]:
                return False, details
        
        return True, details
    
    def get_repository_info(self, repo_url: str, verify_existence: bool = True) -> Dict:
        """
        Get comprehensive information about a repository from its URL.
        
        Args:
            repo_url: The repository URL
            verify_existence: Whether to verify if the repository exists
            
        Returns:
            Dictionary with repository information
        """
        is_valid, details = self.validate_repo_url(repo_url, verify_existence=verify_existence)
        
        if not is_valid:
            return {
                "valid": False,
                "error": details["validation_steps"][-1]["message"],
                "details": details
            }
        
        # If valid, we can add more information
        result = {
            "valid": True,
            "provider": details["provider"],
            "username": details["username"],
            "repo_name": details["repo_name"],
            "url_type": details["url_type"],
            "clone_url": self._get_preferred_clone_url(details),
            "web_url": self._get_web_url(details),
            "api_url": self._get_api_url(details) if self._supports_api(details["provider"]) else None,
            "warnings": details["warnings"]
        }
        
        return result
    
    def validate_many(self, repo_urls: List[str], verify_existence: bool = False) -> Dict[str, Dict]:
        """
        Validate multiple repository URLs at once.
        
        Args:
            repo_urls: List of repository URLs to validate
            verify_existence: Whether to verify if the repositories exist
            
        Returns:
            Dictionary mapping each URL to its validation result
        """
        results = {}
        for url in repo_urls:
            is_valid, details = self.validate_repo_url(url, verify_existence=verify_existence)
            results[url] = {
                "valid": is_valid,
                "details": details
            }
        return results
    
    def _check_basic_format(self, url: str) -> Tuple[bool, str]:
        """Check if the URL has basic valid format."""
        if not url:
            return False, "URL is empty"
        
        valid_prefixes = ('http://', 'https://', 'git@', 'git://')
        if not any(url.startswith(prefix) for prefix in valid_prefixes):
            return False, "URL must start with http://, https://, git@, or git://"
        
        if url.startswith(('http://', 'https://')):
            try:
                result = urllib.parse.urlparse(url)
                if not all([result.scheme, result.netloc]):
                    return False, "URL is missing scheme or host"
            except Exception as e:
                return False, f"Failed to parse URL: {str(e)}"
        
        return True, "Basic format is valid"
    
    def _check_http_url_structure(self, url: str) -> Tuple[bool, str]:
        """Check if HTTP(S) URL has valid structure for a Git repository."""
        # Generic pattern for other Git hosts
        generic = r'^https?://[^/]+/[^/]+/[^/]+(/.*)?$'
        
        # Check against known patterns first
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.netloc.lower()
        
        if hostname in self.provider_patterns:
            if re.match(self.provider_patterns[hostname], url):
                return True, f"Valid {hostname} repository URL format"
            else:
                return False, f"Invalid {hostname} repository URL format"
        
        # Fall back to generic pattern
        if re.match(generic, url):
            return True, "Valid generic repository URL format"
        else:
            return False, "URL doesn't match expected repository path format"
    
    def _check_ssh_url_structure(self, url: str) -> Tuple[bool, str]:
        """Check if SSH URL has valid structure for a Git repository."""
        # Pattern for SSH format - git@domain:user/repo.git
        ssh_pattern = r'^git@([^:]+):([^/]+)/([^/]+)\.git$'
        ssh_pattern_no_git = r'^git@([^:]+):([^/]+)/([^/]+)$'
        
        if re.match(ssh_pattern, url) or re.match(ssh_pattern_no_git, url):
            return True, "Valid SSH repository URL format"
        else:
            return False, "Invalid SSH repository URL format"
    
    def _check_git_protocol_structure(self, url: str) -> Tuple[bool, str]:
        """Check if Git protocol URL has valid structure."""
        # Pattern for git:// protocol
        git_pattern = r'^git://([^/]+)/([^/]+)/([^/]+)(\.git)?$'
        
        if re.match(git_pattern, url):
            return True, "Valid Git protocol URL format"
        else:
            return False, "Invalid Git protocol URL format"
    
    def _extract_provider_info(self, url: str, url_type: str) -> Tuple[bool, Dict]:
        """Extract provider, username and repository name from URL."""
        info = {
            "provider": None,
            "username": None,
            "repo_name": None
        }
        
        try:
            if url_type == "http":
                parsed = urllib.parse.urlparse(url)
                hostname = parsed.netloc.lower()
                
                # Handle different providers
                path_parts = parsed.path.strip('/').split('/')
                
                if hostname == "github.com":
                    info["provider"] = "GitHub"
                    if len(path_parts) >= 2:
                        info["username"] = path_parts[0]
                        # Remove .git extension if present
                        info["repo_name"] = path_parts[1].replace('.git', '')
                    
                elif hostname == "gitlab.com":
                    info["provider"] = "GitLab"
                    if len(path_parts) >= 2:
                        info["username"] = path_parts[0]
                        info["repo_name"] = path_parts[1].replace('.git', '')
                    
                elif hostname == "bitbucket.org":
                    info["provider"] = "Bitbucket"
                    if len(path_parts) >= 2:
                        info["username"] = path_parts[0]
                        info["repo_name"] = path_parts[1].replace('.git', '')
                    
                elif hostname == "dev.azure.com":
                    info["provider"] = "Azure DevOps"
                    if len(path_parts) >= 3:
                        info["username"] = path_parts[0]
                        info["repo_name"] = path_parts[2].replace('.git', '')
                    
                else:
                    info["provider"] = hostname
                    if len(path_parts) >= 2:
                        info["username"] = path_parts[0]
                        info["repo_name"] = path_parts[1].replace('.git', '')
                    
            elif url_type == "ssh":
                # git@github.com:username/repo.git format
                match = re.match(r'^git@([^:]+):([^/]+)/([^/\.]+)(\.git)?$', url)
                if match:
                    hostname, username, repo_name, _ = match.groups()
                    info["provider"] = self._hostname_to_provider(hostname)
                    info["username"] = username
                    info["repo_name"] = repo_name
                    
            elif url_type == "git":
                # git://github.com/username/repo.git format
                match = re.match(r'^git://([^/]+)/([^/]+)/([^/\.]+)(\.git)?$', url)
                if match:
                    hostname, username, repo_name, _ = match.groups()
                    info["provider"] = self._hostname_to_provider(hostname)
                    info["username"] = username
                    info["repo_name"] = repo_name
                    
            # Check if extraction succeeded
            if not all([info["provider"], info["username"], info["repo_name"]]):
                return False, "Failed to extract repository information"
                
            return True, info
            
        except Exception as e:
            self.logger.error(f"Error extracting provider info: {str(e)}")
            return False, f"Error parsing URL: {str(e)}"
    
    def _hostname_to_provider(self, hostname: str) -> str:
        """Convert hostname to provider name."""
        return self.provider_map.get(hostname, hostname)
    
    def _verify_repository_existence(self, url: str, details: Dict) -> Tuple[bool, str]:
        """Verify if the repository actually exists."""
        provider = details.get("provider")
        username = details.get("username")
        repo_name = details.get("repo_name")
        
        if details["url_type"] == "http":
            try:
                # For public repos, we can check if the URL is accessible
                response = requests.head(url, allow_redirects=True, timeout=5)
                if response.status_code == 200:
                    return True, "Repository exists and is accessible"
                elif response.status_code == 404:
                    return False, "Repository not found (404)"
                else:
                    return False, f"Repository check failed with status code: {response.status_code}"
            except RequestException as e:
                return False, f"Failed to verify repository: {str(e)}"
        else:
            # For SSH/Git protocol URLs, we can try a git ls-remote
            try:
                result = subprocess.run(
                    ["git", "ls-remote", url],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return True, "Repository exists and is accessible"
                else:
                    return False, f"Repository not accessible: {result.stderr.strip()}"
            except subprocess.SubprocessError as e:
                return False, f"Failed to verify repository: {str(e)}"
    
    def _get_preferred_clone_url(self, details: Dict) -> str:
        """Get the preferred URL for cloning (HTTPS)."""
        provider = details["provider"].lower()
        username = details["username"]
        repo_name = details["repo_name"]
        
        if "github" in provider:
            return f"https://github.com/{username}/{repo_name}.git"
        elif "gitlab" in provider:
            return f"https://gitlab.com/{username}/{repo_name}.git"
        elif "bitbucket" in provider:
            return f"https://bitbucket.org/{username}/{repo_name}.git"
        else:
            # If we can't determine a specific format, return the original URL
            return details["normalized_url"]
    
    def _get_web_url(self, details: Dict) -> str:
        """Get the web URL for the repository."""
        provider = details["provider"].lower()
        username = details["username"]
        repo_name = details["repo_name"]
        
        if "github" in provider:
            return f"https://github.com/{username}/{repo_name}"
        elif "gitlab" in provider:
            return f"https://gitlab.com/{username}/{repo_name}"
        elif "bitbucket" in provider:
            return f"https://bitbucket.org/{username}/{repo_name}"
        else:
            # Use a generic approach if provider is unknown
            parts = details["normalized_url"].split("://")
            if len(parts) > 1 and parts[0] in ["http", "https"]:
                return details["normalized_url"].rstrip(".git")
            elif "url_type" in details and details["url_type"] == "ssh":
                hostname = details["normalized_url"].split("@")[1].split(":")[0]
                return f"https://{hostname}/{username}/{repo_name}"
            else:
                return None
    
    def _get_api_url(self, details: Dict) -> Optional[str]:
        """Get the API URL for the repository."""
        provider = details["provider"].lower()
        username = details["username"]
        repo_name = details["repo_name"]
        
        if "github" in provider:
            return f"https://api.github.com/repos/{username}/{repo_name}"
        elif "gitlab" in provider:
            return f"https://gitlab.com/api/v4/projects/{username}%2F{repo_name}"
        elif "bitbucket" in provider:
            return f"https://api.bitbucket.org/2.0/repositories/{username}/{repo_name}"
        else:
            return None
    
    def _supports_api(self, provider: str) -> bool:
        """Check if we support API for this provider."""
        return provider in self.api_supported_providers
    
    def get_clone_commands(self, repo_url: str, protocol: str = "https") -> Dict:
        """
        Generate git clone commands for the repository.
        
        Args:
            repo_url: The repository URL
            protocol: The preferred protocol ('https' or 'ssh')
            
        Returns:
            Dictionary with clone commands
        """
        is_valid, details = self.validate_repo_url(repo_url)
        
        if not is_valid:
            return {
                "valid": False,
                "error": details["validation_steps"][-1]["message"]
            }
        
        username = details["username"]
        repo_name = details["repo_name"]
        provider = details["provider"].lower()
        
        result = {"valid": True}
        
        # HTTPS clone command
        if "github" in provider:
            result["https"] = f"git clone https://github.com/{username}/{repo_name}.git"
            result["ssh"] = f"git clone git@github.com:{username}/{repo_name}.git"
        elif "gitlab" in provider:
            result["https"] = f"git clone https://gitlab.com/{username}/{repo_name}.git"
            result["ssh"] = f"git clone git@gitlab.com:{username}/{repo_name}.git"
        elif "bitbucket" in provider:
            result["https"] = f"git clone https://bitbucket.org/{username}/{repo_name}.git"
            result["ssh"] = f"git clone git@bitbucket.org:{username}/{repo_name}.git"
        else:
            # Generic approach
            if details["url_type"] == "http":
                result["https"] = f"git clone {details['normalized_url']}"
                
                # Try to construct SSH URL
                parsed = urllib.parse.urlparse(details["normalized_url"])
                hostname = parsed.netloc
                result["ssh"] = f"git clone git@{hostname}:{username}/{repo_name}.git"
            elif details["url_type"] == "ssh":
                result["ssh"] = f"git clone {details['normalized_url']}"
                
                # Try to construct HTTPS URL
                hostname = details["normalized_url"].split("@")[1].split(":")[0]
                result["https"] = f"git clone https://{hostname}/{username}/{repo_name}.git"
            else:
                result["https"] = f"git clone {details['normalized_url']}"
                result["ssh"] = f"git clone {details['normalized_url']}"
        
        # Set preferred command
        result["preferred"] = result.get(protocol, result["https"])
        
        return result


# Example usage
if __name__ == "__main__":
    validator = RepositoryValidator()
    
    test_urls = [
        "https://github.com/tensorflow/tensorflow",
        "git@github.com:django/django.git",
        "git://github.com/torvalds/linux.git",
        "https://gitlab.com/gitlab-org/gitlab",
        "https://bitbucket.org/atlassian/atlaskit",
        "http://invalid-url",
        "git@github.com:nonexistent/notarealrepo.git"
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        valid, details = validator.validate_repo_url(url)
        print(f"Valid: {valid}")
        
        if valid:
            info = validator.get_repository_info(url, verify_existence=False)
            print(f"Provider: {info['provider']}")
            print(f"Username: {info['username']}")
            print(f"Repository name: {info['repo_name']}")
            print(f"Clone URL: {info['clone_url']}")
            print(f"Web URL: {info['web_url']}")
            
            clone_commands = validator.get_clone_commands(url)
            if clone_commands["valid"]:
                print(f"HTTPS clone: {clone_commands['https']}")
                print(f"SSH clone: {clone_commands['ssh']}")
        else:
            print(f"Validation failed: {details['validation_steps'][-1]['message']}")