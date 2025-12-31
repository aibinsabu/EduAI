try:
    from transformers import pipeline, T5Tokenizer
    print("SUCCESS: Transformers imported.")
    
    # Try initializing the tokenizer as that triggered the error
    tokenizer = T5Tokenizer.from_pretrained("valhalla/t5-base-qg-hl")
    print("SUCCESS: Tokenizer initialized.")
    
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
