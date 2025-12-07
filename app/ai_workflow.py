# app/ai_workflow.py
from app.perplexity_ai import ask_perplexity
import json

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

def generate_health_scores(text: str) -> dict:
    """
    Analyze a health report and generate scores for:
    - Overall Health (0-100)
    - Physical Health (0-100)
    - Mental Health (0-100)
    - Internal Health (0-100)
    """
    prompt = (
        "You are a health analytics AI. "
        "Based on the following health report, assign scores (0-100) for:\n"
        "1. Overall Health Score\n"
        "2. Physical Health Score\n"
        "3. Mental Health Score\n"
        "4. Internal Health Score\n\n"
        "Where 100 = excellent, 70-99 = good, 50-69 = fair, below 50 = poor.\n"
        "Be realistic and slightly conservative in scoring.\n\n"
        "Return ONLY valid JSON (no markdown, no extra text) like this:\n"
        '{"overall": 75, "physical": 80, "mental": 70, "internal": 65}\n\n'
        f"Health report text:\n{text[:8000]}"
    )
    
    response=ask_perplexity(prompt)
    
    try:
        scores = json.loads(response.strip())
        return{
            "overall_health_score": float(scores.get("overall", 0)),
            "physical_health_score": float(scores.get("physical", 0)),
            "mental_health_score": float(scores.get("mental", 0)),
            "internal_health_score": float(scores.get("internal", 0)),
        }
    except json.JSONDecodeError:
        return {
            "overall_health_score": 0.0,
            "physical_health_score": 0.0,
            "mental_health_score": 0.0,
            "internal_health_score": 0.0,
        }