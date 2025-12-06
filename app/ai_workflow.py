# app/ai_workflow.py
from app.perplexity_ai import ask_perplexity

def summarize_health_report(text: str) -> str:
    """
    Take raw text from a health report and return a patient‑friendly summary using Perplexity.
    """
    prompt = (
        "You are a kind, calm medical explainer.\n"
        "The user has uploaded a medical or health report.\n"
        "Task for you:\n"
        "- Read the report text.\n"
        "- Explain the key findings in simple, everyday language.\n"
        "- Clearly mention what seems normal and what might be abnormal.\n"
        "- Avoid giving diagnosis or treatment; just explain.\n"
        "- End with this sentence: 'Please consult your doctor for medical advice.'\n\n"
        f"Health report text:\n{text[:8000]}"
    )

    summary = ask_perplexity(prompt)
    return summary
