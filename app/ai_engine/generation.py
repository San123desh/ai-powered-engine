from app.ai_engine.utils import get_ollama_client
from cachetools import LRUCache
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    prompt = f"Complete the following {language} function by providing only the function body as plain code (do not repeat the function signature, do not include markdown, code blocks, comments, or explanations). The output should be the exact code to append after the function signature, with proper indentation, and must be syntactically correct and return an appropriate value:\n{code}\nReturn only the function body, nothing else."

    # Call Ollama to generate function
    response = ollama_client.generate(model="codellama", prompt=prompt)
    generated_code = response['response'].strip()

    # Log the raw response for debugging
    logger.debug(f"Raw response from Ollama: {repr(generated_code)}")

    # Post-process to remove markdown, comments, and explanations
    lines = generated_code.split("\n")
    code_lines = []
    in_code_block = False
    for line in lines:
        line = line.strip()
        # Skip markdown code block markers
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        # Skip comments and empty lines outside code blocks
        if not in_code_block and (line.startswith("#") or line.startswith("//") or not line):
            continue
        # Skip explanatory text (heuristic: lines without indentation are likely explanations)
        if not in_code_block and not line.startswith(" ") and not line.startswith("\t"):
            continue
        # Add the actual code line
        code_lines.append(line)

    generated_code = "\n".join(code_lines).strip()

    # Log the processed code
    logger.debug(f"Processed code: {repr(generated_code)}")

    # If the generated code is empty or invalid, use a placeholder
    if not generated_code or generated_code.isspace():
        if language == "python":
            generated_code = "    return None  # Generated placeholder"
        elif language == "javascript":
            generated_code = "    return null;  // Generated placeholder\n}"
        else:
            generated_code = "// Generated code for unsupported language"
    else:
        # Ensure the generated code is a continuation (remove the input code if present)
        code_stripped = code.strip()
        if generated_code.startswith(code_stripped):
            generated_code = generated_code[len(code_stripped):].strip()

        # For JavaScript, ensure the closing brace is included if needed
        if language == "javascript" and not generated_code.endswith("}"):
            generated_code = f"{generated_code}\n}}"

    # Combine the input signature with the generated body for a ready-to-use function
    final_code = f"{code}\n{generated_code}"

    # Cache the result
    generation_cache[cache_key] = final_code
    return final_code

