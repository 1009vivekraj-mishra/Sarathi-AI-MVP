"""backend/learning_engine.py
Generate concise learning suggestions based on retrieved sources.
"""
from typing import List, Dict

# Simple static tip library (could be expanded)
TIP_LIBRARY = {
    "safety": ["Always wear PPE before accessing machinery.", "Check emergency stop functionality daily."],
    "maintenance": ["Lubricate moving parts every 200 hrs.", "Record downtime in the log sheet."],
    "operations": ["Follow the standard start‑up checklist.", "Verify sensor calibrations before run."]
}

def _extract_skill_category(sources: List[Dict[str, str]]) -> str:
    """Very naive skill categorisation based on keywords in source paths.
    In a real system this would use a classifier.
    """
    text = " ".join([src.get("source", "").lower() for src in sources])
    for cat in TIP_LIBRARY.keys():
        if cat in text:
            return cat
    return "general"

def generate_learning_suggestions(sources: List[Dict[str, str]], max_items: int = 2) -> List[str]:
    """Return up to `max_items` suggestions.
    Preference order: SOP title from source → tip from library → next skill recommendation.
    """
    suggestions: List[str] = []
    # 1. SOP snippet title (use filename)
    if sources:
        first_source = sources[0].get("source", "")
        if first_source:
            title = first_source.split('/')[-1]
            suggestions.append(f"Review: {title}")
    # 2. Tip based on detected skill category
    skill = _extract_skill_category(sources)
    tips = TIP_LIBRARY.get(skill, [])
    if tips:
        suggestions.append(tips[0])
    # 3. Next skill recommendation (placeholder)
    if len(suggestions) < max_items:
        next_skill = "maintenance" if skill != "maintenance" else "operations"
        suggestions.append(f"Consider exploring {next_skill} procedures.")
    return suggestions[:max_items]
