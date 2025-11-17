from .perplexity_ai import ask_perplexity

def summarize_document(text):
    prompt = (
        "Please summarize the following business document and "
        "highlight main business entities, dates, and action items. "
        "For medical documents, provide differential diagnoses for the disease"
        "Text:\n" + text[:4000]  # Limit for demo; slice as needed for length
    )
    return ask_perplexity(prompt)