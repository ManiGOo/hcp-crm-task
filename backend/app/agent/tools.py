# backend/app/agent/tools.py
from langchain_core.tools import tool
from typing import Dict, Any, Optional, Union
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

    # --- Preprocessing for interaction_type ---
    processed_interaction_type = interaction_type.lower()
    if processed_interaction_type == "virtual meeting":
        processed_interaction_type = "virtual" # Convert to 'virtual' to match enum before title()
    
    # FORCE LOWERCASE to match your Pydantic Enums and Postgres Types
    data = {
        "hcp_name": hcp_name,
        "attendees": attendees, # Include attendees in data
        "date": interaction_date,
        "time": time,
        "interaction_type": processed_interaction_type.title(), # Ensures 'Meeting', 'Virtual', etc.
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
    interaction_id: Union[int, str],
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
) -> Dict[str, Any]:
    """
    Tool to edit an existing HCP interaction.
    You MUST provide the `interaction_id` of the interaction to edit.
    If the user says "edit the last one" or "edit that one", look at the conversation history for the ID of the most recently logged interaction.
    Only provide the fields that need updating.
    """
    try:
        interaction_id = int(interaction_id)
    except (ValueError, TypeError):
        # Handle cases where conversion fails, maybe return an error message
        # For now, this assumes the LLM provides a number-like string or an int
        pass

    updates = {k: v for k, v in locals().items() if v is not None and k != "interaction_id"}

    print(f"=== TOOL: edit_interaction called for ID {interaction_id} ===")
    print("Updates:", updates)

    # Instead of returning a string, return structured data for the main endpoint to process
    return {
        "tool_name": "edit_interaction",
        "interaction_id": interaction_id,
        "updates": updates,
    }


@tool
def search_hcp(name_query: str) -> Dict[str, Any]:
    """Search for HCP details by name or specialty.
    The `name_query` should be the HCP's name or a part of it.
    """
    print(f"=== TOOL: search_hcp called with name_query: {name_query} ===")
    return {
        "tool_name": "search_hcp",
        "query": name_query,
    }


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
def check_compliance(topics: str) -> Dict[str, Any]:
    """Compliance check for discussed topics."""
    compliance_message = "All topics compliant."
    if any(word in topics.lower() for word in ["off-label", "price", "discount"]):
        compliance_message = "Compliance WARNING: Review with QA before logging."
    
    print(f"=== TOOL: check_compliance called with topics: {topics} ===")
    return {
        "tool_name": "check_compliance",
        "compliance_message": compliance_message,
    }

@tool
def set_user_name(name: str) -> Dict[str, Any]:
    """Sets the name of the current user for personalized interactions."""
    print(f"=== TOOL: set_user_name called with name: {name} ===")
    return {
        "tool_name": "set_user_name",
        "user_name": name,
    }

@tool
def extract_interaction_data(
    hcp_name: str,
    attendees: Optional[str] = None,
    date: Optional[str] = None,  # IMPORTANT: Must be in YYYY-MM-DD format.
    time: Optional[str] = None,
    interaction_type: str = "meeting",  # Default to lowercase
    topics: Optional[str] = None,
    materials_distributed: Optional[str] = None,
    outcomes: str = "neutral",
    follow_up: Optional[str] = None,
    summary: Optional[str] = None
) -> Dict[str, Any]:
    """Extracts structured data for an HCP interaction from the user's input."""
    data = {
        "hcp_name": hcp_name,
        "attendees": attendees,
        "date": date,
        "time": time,
        "interaction_type": interaction_type,
        "topics": topics,
        "materials_distributed": materials_distributed,
        "outcomes": outcomes,
        "follow_up": follow_up,
        "summary": summary,
    }
    print(f"=== TOOL: extract_interaction_data called with data: {data} ===")
    return {
        "tool_name": "extract_interaction_data",
        "extracted_data": data,
    }