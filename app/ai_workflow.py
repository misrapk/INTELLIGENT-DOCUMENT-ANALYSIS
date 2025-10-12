from .perplexity_ai import ask_perplexity

def summarize_document(text):
    prompt = (
        "Please summarize the following business document and "
        "highlight main business entities, dates, and action items. "
        "Text:\n" + text[:4000]  # Limit for demo; slice as needed for length
    )
    return ask_perplexity(prompt)