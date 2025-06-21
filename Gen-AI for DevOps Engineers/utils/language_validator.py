
supported_languages = [
    "python", "javascript", "java", "csharp", "c++", "ruby", "go",
    "typescript", "php", "swift", "kotlin", "rust", "scala","js",'c#'
]


def validate_language(language="python"):
    """
    Validates the programming language input.

    Args:
        language (str): The programming language to validate.

    Returns:
        str: The validated programming language.
    
    Raises:
        ValueError: If the language is not supported.
    """
  
    if language.lower() not in supported_languages:
        raise ValueError(f"❌   ERROR: Unsupported programming language: {language} \n"
                         f"Supported languages are: {', '.join(supported_languages)}")

    return language.lower()