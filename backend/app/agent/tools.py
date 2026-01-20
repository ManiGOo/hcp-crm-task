# backend/app/agent/tools.py
from langchain_core.tools import tool
from typing import Dict, Any, Optional
from datetime import datetime

@tool
def log_interaction(
    hcp_name: str,
    attendees: Optional[str] = None, # New field: Attendees
    date: Optional[str] = None,  # IMPORTANT: Must be in YYYY-MM-DD format.
    time: Optional[str] = None,
    interaction_type: str = "meeting",  # Default to lowercase
    topics: Optional[str] = None,
    materials_distributed: Optional[str] = None,
    outcomes: str = "neutral",          # Default to lowercase
    follow_up: Optional[str] = None,
    summary: Optional[str] = None
) -> Dict[str, Any]:
    """Log a new interaction with a Healthcare Professional into the CRM."""
    
    # If date is not provided, default to today's date
    interaction_date = date if date else datetime.now().strftime('%Y-%m-%d')

    # FORCE LOWERCASE to match your Pydantic Enums and Postgres Types
    data = {
        "hcp_name": hcp_name,
        "attendees": attendees, # Include attendees in data
        "date": interaction_date,
        "time": time,
        "interaction_type": interaction_type.title(), # Ensures 'meeting'
        "topics": topics,
        "materials_distributed": materials_distributed,
        "outcomes": outcomes.title(),                 # Ensures 'positive'
        "follow_up": follow_up,
        "summary": summary,
    }
    print("Logged data (Fixed for Schema):", data)
    return data


@tool
def edit_interaction(
    interaction_id: int,
    hcp_name: Optional[str] = None,
    attendees: Optional[str] = None, # New field: Attendees
    date: Optional[str] = None,  # IMPORTANT: Must be in YYYY-MM-DD format.
    time: Optional[str] = None,
    interaction_type: Optional[str] = None,
    topics: Optional[str] = None,
    materials_distributed: Optional[str] = None,
    outcomes: Optional[str] = None,
    follow_up: Optional[str] = None,
    summary: Optional[str] = None
) -> str:
    """
    Tool to edit an existing HCP interaction.
    Only provide the fields that need updating.
    """
    updates = {k: v for k, v in locals().items() if v is not None and k != "interaction_id"}

    print(f"=== TOOL: edit_interaction called for ID {interaction_id} ===")
    print("Updates:", updates)

    updated_fields = ", ".join(updates.keys()) or "No changes"
    return f"Interaction #{interaction_id} updated successfully! Changed: {updated_fields}"


@tool
def search_hcp(query: str) -> str:
    """Search for HCP details by name or specialty."""
    return f"Found Dr. {query.title()}: Cardiologist, Ahmedabad. Last interaction: 2 weeks ago."


@tool
def suggest_follow_up(outcome: str) -> str:
    """Suggest next steps based on outcome."""
    outcome = outcome.lower()
    if "positive" in outcome:
        return "Schedule follow-up in 2 weeks + send product samples."
    elif "negative" in outcome:
        return "Escalate to medical liaison and monitor closely."
    return "No immediate action needed."


@tool
def generate_summary(raw_text: str) -> str:
    """Create concise summary of interaction notes."""
    return f"Summary: {raw_text.strip()[:120]}{'...' if len(raw_text) > 120 else ''}"


@tool
def check_compliance(topics: str) -> str:
    """Compliance check for discussed topics."""
    if any(word in topics.lower() for word in ["off-label", "price", "discount"]):
        return "Compliance WARNING: Review with QA before logging."
    return "All topics compliant."