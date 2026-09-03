from transformers import MarianMTModel, MarianTokenizer
import re

def clean_col(c):
    return c.replace("_", " ").title()

model_name = "Helsinki-NLP/opus-mt-en-es"
print(f"Loading {model_name}...")
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

cols = ["JE_CATEGORY", "JE_SOURCE", "CREATED_IN_GL", "POSTED_BY_GL", "JE_HEADER_ID", "CODE_COMBINATION"]
cleaned = [clean_col(c) for c in cols]

inputs = tokenizer(cleaned, return_tensors="pt", padding=True)
translated = model.generate(**inputs)
results = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]

print(results)
