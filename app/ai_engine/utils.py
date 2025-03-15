from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


#load CodeBERT 
model_name = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
model = AutoModelForCausalLM.from_pretrained(model_name, is_decoder=True)


#quantize the model for faster inference on cpu
model.eval()
model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

def get_codebert_model():
    """
    Return the pre-loaded CodeBERT model and tokenizer.
    """
    return model, tokenizer