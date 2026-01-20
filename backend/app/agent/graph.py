# backend/app/agent/graph.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv

load_dotenv()

from .tools import (
    log_interaction,
    edit_interaction,
    search_hcp,
    suggest_follow_up,
    generate_summary,
    check_compliance,
)

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    interaction_data: Dict[str, Any]  # ← this will hold extracted fields
    raw_user_input: str # Store the initial human message

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
)

tools = [log_interaction, edit_interaction, search_hcp, suggest_follow_up, generate_summary, check_compliance]
llm_with_tools = llm.bind_tools(tools)

# Strong prompt that FORCES extraction + tool use + final reply
system_prompt = """
You are an intelligent AI assistant for pharmaceutical field representatives.
Your primary goal is to parse the user's natural language description of an HCP interaction and:

1. Extract structured data for the form:
   - hcp_name: Full name of the doctor/HCP
   - attendees: Comma-separated list of other attendees (e.g., "Dr. Jones, Nurse Anne")
   - date: Date in YYYY-MM-DD format
   - time: Time in HH:MM format
   - interaction_type: Meeting, Call, Email, or Virtual
   - topics: Main topics discussed (comma-separated)
   - materials_distributed: List of materials/samples given (or 'None')
   - outcomes: Positive, Neutral, or Negative
   - follow_up: Any follow-up actions planned
   - summary: Short 1-2 sentence summary, GENERATED AUTOMATICALLY IF NOT PROVIDED.

2. Store extracted data in the 'interaction_data' state field as a dictionary.

3. If the user wants to log/save, call the 'log_interaction' tool with the extracted data.

4. Always respond to the user with a clear, friendly confirmation message.
   Example: "Got it! I extracted the following details: Dr. Patel, Meeting, Positive outcome... Ready to log?"

Be precise, professional, and helpful.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

def agent_node(state: AgentState):
    chain = prompt | llm_with_tools
    response = chain.invoke(state["messages"])
    return {
        "messages": [response],
        "interaction_data": state.get("interaction_data", {}),  # preserve previous
        "raw_user_input": state["messages"][0].content if state["messages"] and isinstance(state["messages"][0], HumanMessage) else ""
    }

tool_node = ToolNode(tools)

def generate_summary_node(state: AgentState):
    interaction_data = state["interaction_data"]
    raw_user_input = state.get("raw_user_input", "") # Use raw user input for summary generation

    if not interaction_data.get("summary"): # If summary is missing, generate it
        # Combine relevant fields to create raw_text for summary generation
        summary_raw_text_parts = []
        if interaction_data.get("hcp_name"):
            summary_raw_text_parts.append(f"HCP: {interaction_data['hcp_name']}")
        if interaction_data.get("interaction_type"):
            summary_raw_text_parts.append(f"Type: {interaction_data['interaction_type']}")
        if interaction_data.get("topics"):
            summary_raw_text_parts.append(f"Topics: {interaction_data['topics']}")
        if interaction_data.get("materials_distributed"):
            summary_raw_text_parts.append(f"Materials: {interaction_data['materials_distributed']}")
        if interaction_data.get("outcomes"):
            summary_raw_text_parts.append(f"Outcome: {interaction_data['outcomes']}")
        if raw_user_input: # Fallback to raw user input if other fields are sparse
            summary_raw_text_parts.append(f"Original request: {raw_user_input}")


        summary_raw_text = ". ".join(filter(None, summary_raw_text_parts))

        # Call the generate_summary tool
        generated_summary = generate_summary.func(raw_text=summary_raw_text) # Access the underlying function
        
        interaction_data["summary"] = generated_summary.replace("Summary: ", "") # Remove "Summary: " prefix
    
    return {"interaction_data": interaction_data}

def update_extracted_data_node(state: AgentState):
    """Extract data from last AI message if present"""
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "additional_kwargs") and "tool_calls" in last_msg.additional_kwargs:
        # If tool was called, assume extraction happened
        pass
    # In real: you can parse LLM output here for extraction
    # For now, rely on prompt to encourage tool call with data
    return state

workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_node("generate_summary_node", generate_summary_node) # Add the new node
workflow.add_node("update_data", update_extracted_data_node)

workflow.set_entry_point("agent")
# Condition to go to generate_summary_node if summary is missing, else to tools
workflow.add_conditional_edges(
    "agent",
    lambda state: "generate_summary_node" if not state["interaction_data"].get("summary") else "tools",
    {"generate_summary_node": "generate_summary_node", "tools": "tools"}
)

workflow.add_edge("generate_summary_node", "tools") # After generating summary, proceed to tools
workflow.add_edge("tools", "update_data")
workflow.add_edge("update_data", END)

graph = workflow.compile()