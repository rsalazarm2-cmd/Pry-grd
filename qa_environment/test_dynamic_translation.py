import asyncio
from src.ai_translator.infrastructure.marian_mt_translator import MarianMTTranslator
from src.ai_translator.application.translate_columns_use_case import TranslateColumnsUseCase

def test():
    print("Loading Translator...")
    translator = MarianMTTranslator()
    use_case = TranslateColumnsUseCase(translator)
    
    cols = [
        "JE_CATEGORY",
        "JE_SOURCE", 
        "CREATED_IN_GL",
        "POSTED_BY_GL",
        "JE_HEADER_ID",
        "AMOUNT",
        "amount",
        "Amount"
    ]
    print("Executing use case...")
    result = use_case.execute(cols)
    print("Mapping Result:")
    for k, v in result.suggested_mapping.items():
        print(f"  {k} -> {v}")

if __name__ == "__main__":
    test()
