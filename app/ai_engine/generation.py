# # from transformers import AutoModelForCausalLM, AutoTokenizer
# # from app.ai_engine.utils import get_codebert_model

# # model, tokenizer = get_codebert_model()

# # def generate_function(code: str, context: dict) -> str:
# #     """Generate a complete function or code block using CodeBERT."""
# #     language = context.get("language", "python").lower()
# #     input_text = f"{code} # {language} # Complete the function"
# #     inputs = tokenizer(input_text, return_tensors="pt", max_length=128, truncation=True, padding="max_length")
# #     outputs = model.generate(
# #         **inputs,
# #         max_length=200,
# #         num_return_sequences=1,
# #         do_sample=True,
# #         top_k=50,
# #         top_p=0.95,
# #         temperature=0.7
# #     )
# #     generated_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
# #     generated_code = generated_code[len(input_text):].strip()

# #     # Clean up the generated code
# #     lines = generated_code.split("\n")
# #     cleaned_code = []
# #     for line in lines:
# #         line = line.strip()
# #         if line and not line.startswith("#"):  # Remove comments and empty lines
# #             cleaned_code.append(line)
# #         if len(cleaned_code) >= 2:  # Limit to a few lines for simplicity
# #             break
# #     generated_code = "\n".join(cleaned_code)

# #     # Fallback to placeholder if generated code is empty or invalid
# #     if not generated_code or "#" in generated_code:
# #         if language == "python":
# #             return f"{code}\n    return None  # Generated placeholder"
# #         elif language == "javascript":
# #             return f"{code}\n    return null;  // Generated placeholder\n}}"
# #         else:
# #             return "// Generated code for unsupported language"

# #     return generated_code






# import logging
# from transformers import AutoModelForCausalLM, AutoTokenizer
# from app.ai_engine.utils import get_codebert_model

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Load model and tokenizer (reusing the pre-loaded instance)
# model, tokenizer = get_codebert_model()

# def generate_function(code: str, context: dict) -> str:
#     """Generate a complete function or code block using CodeBERT."""
#     language = context.get("language", "python").lower()
#     input_text = f"{code} # {language} # Complete the function"

#     try:
#     inputs = tokenizer(input_text, return_tensors="pt", max_length=128, truncation=True, padding="max_length")
#     outputs = model.generate(
#         **inputs,
#         max_length=200,
#         num_return_sequences=1,
#         do_sample=True,
#         top_k=50,
#         top_p=0.95,
#         temperature=0.7
#     )
#     generated_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     generated_code = generated_code[len(input_text):].strip()

#     # Clean up the generated code
#     lines = generated_code.split("\n")
#     cleaned_code = []
#     for line in lines:
#         line = line.strip()
#         if line and not line.startswith("#"):  # Remove comments and empty lines
#             cleaned_code.append(line)
#         if len(cleaned_code) >= 2:  # Limit to a few lines for simplicity
#             break
#     generated_code = "\n".join(cleaned_code)

#     # Fallback to placeholder if generated code is empty or invalid
#     if not generated_code or "#" in generated_code:
#         if language == "python":
#             if "def " in code:
#                 return f"{code}\n    return None  # Generated placeholder"
#             else:
#                 return "def placeholder():\n    return 'Generated function'  # Placeholder function"
#         elif language == "javascript":
#             if "function " in code:
#                 return f"{code}\n    return null;  // Generated placeholder\n}}"
#             else:
#                 return "function placeholder() {\n    return 'Generated function';  // Placeholder function\n}"
#         else:
#             return "// Generated code for unsupported language"

#     return generated_code



import logging
from app.ai_engine.utils import get_codebert_model
from transformers import AutoModelForCausalLM, AutoTokenizer
from cachetools import LRUCache

#initialize cache 
generation_cache = LRUCache(maxsize=1000)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load model and tokenizer (reusing the pre-loaded instance)
model, tokenizer = get_codebert_model()

def generate_function(code: str, context: dict) -> str:
    """Generate a complete function or code block using CodeBERT."""

    #create a cache key based on inputs
    cache_key = (code, tuple(sorted(context.items())))

    if cache_key in generation_cache:
        return generation_cache[cache_key]

    language = context.get("language", "python").lower()
    input_text = f"{code} # {language} # Complete the function"
    
    try:
        inputs = tokenizer(input_text, return_tensors="pt", max_length=128, truncation=True, padding="max_length")
        outputs = model.generate(
            **inputs,
            max_length=200,
            num_return_sequences=1,
            do_sample=True,
            top_k=50, 
            top_p=0.95,
            temperature=0.7
        )
        generated_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.debug(f"Raw CodeBERT output: {generated_code}")  # Debug log
        
        # Extract the generated part after the input
        generated_code = generated_code[len(input_text):].strip()

        # Clean up the generated code
        lines = generated_code.split("\n")
        cleaned_code = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):  # Remove comments and empty lines
                cleaned_code.append(line)
            if len(cleaned_code) >= 2:  # Limit to a few lines for simplicity
                break
        generated_code = "\n".join(cleaned_code)

        # Validate the generated code for the language
        if language == "javascript":
            # Ensure the generated code contains JavaScript-like syntax (e.g., "return", ";", "}")
            if not ("return" in generated_code or ";" in generated_code or "}" in generated_code):
                raise ValueError("Generated code does not resemble valid JavaScript")
            # Ensure the code ends with a closing brace
            if "function " in code and not generated_code.endswith("}"):
                generated_code = f"{code}\n{generated_code}\n}}"
        elif language == "python":
            # Ensure the generated code contains Python-like syntax (e.g., "return", indentation)
            if not ("return" in generated_code or generated_code.startswith(" ")):
                raise ValueError("Generated code does not resemble valid Python")

        # cache the result
        generation_cache[cache_key] = generated_code
        # If validation passes, return the generated code
        return generated_code

    except Exception as e:
        logger.error(f"CodeBERT generation failed: {str(e)}. Falling back to placeholder logic.")
        # Fallback to placeholder logic if CodeBERT fails or validation fails
        if language == "python":
            if "def " in code:
                return f"{code}\n    return None  # Generated placeholder"
            else:
                return "def placeholder():\n    return 'Generated function'  # Placeholder function"
        elif language == "javascript":
            if "function " in code:
                return f"{code}\n    return null;  // Generated placeholder\n}}"
            else:
                return "function placeholder() {\n    return 'Generated function';  // Placeholder function\n}"
        else:
            return "// Generated code for unsupported language"