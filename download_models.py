import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def download_and_save_model():
    """
    Downloads the FinBERT model and tokenizer from Hugging Face 
    and saves them to a local directory.
    """
    model_name = "ProsusAI/finbert"
    local_path = "./finbert-model"

    if os.path.exists(local_path):
        print(f"Model directory '{local_path}' already exists. Skipping download.")
        return

    print(f"Downloading model and tokenizer for '{model_name}'...")
    
    # Download and save tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.save_pretrained(local_path)
    
    # Download and save model
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.save_pretrained(local_path)
    
    print(f"Model and tokenizer saved to '{local_path}'")

if __name__ == "__main__":
    download_and_save_model()
