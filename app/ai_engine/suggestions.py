from app.ai_engine.utils import get_ollama_client
from cachetools import LRUCache

# Initialize cache (max 1000 entries) to store previously requested suggestions
suggestion_cache = LRUCache(maxsize=1000)

# Get Ollama client
ollama_client = get_ollama_client()

def suggest_code(code, cursor_position, context):
    """
    Generate inline code suggestions using Ollama with caching.
    """
    # Create a cache key based on input parameters
    cache_key = (code, cursor_position, tuple(sorted(context.items())))

    # Check if the result is already cached and return if available
    if cache_key in suggestion_cache:
        return suggestion_cache[cache_key]

    language = context.get("language", "python").lower()
    if cursor_position is None or cursor_position < 0:
        cursor_position = len(code)
    code_prefix = code[:cursor_position].strip()

    # Prepare prompt for Ollama
    prompt = f"Given the following {language} code, provide the next line of code to continue the function (do not include markdown, code blocks, or explanations):\n{code_prefix}\n# Return the next line of code"

    # Call Ollama codellama model to generate suggestion
    response = ollama_client.generate(model="codellama", prompt=prompt)
    suggestion = response['response'].strip()

    # Parse the response to extract the suggestion (remove markdown code blocks)
    lines = suggestion.split("\n")
    suggestion_lines = []
    in_code_block = False
    for line in lines:
        if line.strip() == "```":
            in_code_block = not in_code_block
        elif in_code_block and line.strip():
            suggestion_lines.append(line.strip())
        elif not in_code_block and line.strip():
            suggestion_lines.append(line.strip())
    suggestion = suggestion_lines[0] if suggestion_lines else ""

    # Add indentation for Python(4 spaces: Standard Python indentation) 
    if language == "python" and suggestion:
        suggestion = "    " + suggestion

    # Fallback if suggestion is empty or invalid
    if not suggestion or "#" in suggestion:
        if language == "python":
            suggestion = "    pass  # suggested"
        elif language == "javascript":
            suggestion = "return null;  // Suggested placeholder"
        else:
            suggestion = "// Suggestion for unsupported language"

    # Cache the result
    suggestion_cache[cache_key] = suggestion
    return suggestion