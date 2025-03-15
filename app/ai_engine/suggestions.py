from transformers import AutoModelForCausalLM, AutoTokenizer
from app.ai_engine.utils import get_codebert_model
from cachetools import LRUCache

# Initialize a cache for storing previous code suggestions
suggestion_cache = LRUCache(maxsize=5000)

model, tokenizer = get_codebert_model()

def suggest_code(code: str, cursor_position: int, context: dict) -> str:
    """
    Generate inline code suggestions based on the code, cursor position, and context.
    """

    #create a cache key based on inputs
    cache_key = (code, cursor_position, tuple(sorted(context.items())))

    # Check if the suggestion is already in the cache
    if cache_key in suggestion_cache:
        return suggestion_cache[cache_key]


    # Extract programming language from context (default to Python if not provided)
    language = context.get("language", "python").lower()

    # Extract code before the cursor position
    if cursor_position is None or cursor_position < 0:
        cursor_position = len(code)
    code_prefix = code[:cursor_position].strip()

    # Tokenize code prefix and generate tokenized input
    input_text = f"{code_prefix} # {language}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length= 128, truncation=True, padding="max_length")
    outputs = model.generate(
        **inputs,
        max_length=100,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        # stop_token_id=tokenizer.eos_token_id,
        # pad_token_id=tokenizer.pad_token_id,
        # eos_token_id=tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.9,
        top_k=50,
        top_p=0.95,
    )

    #decode the generated suggestion
    suggestion = tokenizer.decode(outputs[0], skip_special_tokens=True)
    suggestion = suggestion[len(code_prefix):].strip().split('\n')[0]

    #fall back to the original suggestion if there was no suggestion 
    # if not suggestion or "#" in suggestion:
    #     if language == "python":
    #         return "pass # suggested"
    #     elif language == "javascript":
    #         return "return null; // suggested placeholder"
    #     else:
    #         return "// suggestion for unsupported language"
        
    
    # return suggestion

    if not suggestion or "#" in suggestion:
        if language == "python":
            suggestion = "pass  # suggested"
        elif language == "javascript":
            suggestion = "return null;  // Suggested placeholder"
        else:
            suggestion = "// Suggestion for unsupported language"

    # Cache the result
    suggestion_cache[cache_key] = suggestion
    return suggestion






















