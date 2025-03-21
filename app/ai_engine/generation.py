from app.ai_engine.utils import get_ollama_client
from cachetools import LRUCache

# Initialize cache (max 1000 entries)
generation_cache = LRUCache(maxsize=1000)

# Get Ollama client
ollama_client = get_ollama_client()

def generate_function(code: str, context: dict) -> str:
    """
    Generate a complete function using Ollama with caching.
    """
    # Create a cache key based on inputs
    cache_key = (code, tuple(sorted(context.items())))

    # Check cache first
    if cache_key in generation_cache:
        return generation_cache[cache_key]

    language = context.get("language", "python").lower()
    prompt = f"Generate a complete {language} function based on the following partial code. Return only the code continuation, without markdown, code blocks, or explanations:\n{code}\n# Complete the function"

    # Call Ollama to generate function
    response = ollama_client.generate(model="codellama", prompt=prompt)
    generated_code = response['response'].strip()

    # Extract the code continuation (remove markdown and commentary)
    lines = generated_code.split("\n")
    code_lines = []
    in_code_block = False
    for line in lines:
        if line.strip() == "```":
            in_code_block = not in_code_block
        elif in_code_block and line:
            code_lines.append(line)  # Preserve indentation
    generated_code = "\n".join(code_lines).strip()

    # Remove the input code from the output (if present)
    if generated_code.startswith(code.strip()):
        generated_code = generated_code[len(code.strip()):].strip()

    # Fallback to placeholder if generated code is empty or invalid
    if not generated_code or "#" in generated_code:
        if language == "python":
            generated_code = f"{code}\n    return None  # Generated placeholder"
        elif language == "javascript":
            generated_code = f"{code} {{\n    return null;  // Generated placeholder\n}}"
        else:
            generated_code = "// Generated code for unsupported language"

    # Cache the result
    generation_cache[cache_key] = generated_code
    return generated_code