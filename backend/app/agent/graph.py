# backend/app/agent/graph.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
import json # Import json for parsing tool call arguments

load_dotenv()

from .tools import (
    log_interaction,
    edit_interaction,
    search_hcp,
    suggest_follow_up,
    generate_summary,
    check_compliance,
    set_user_name,
    extract_interaction_data,
)

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    interaction_data: Dict[str, Any]  # ← this will hold extracted fields
    raw_user_input: str # Store the initial human message
    db_session: Optional[AsyncSession]
    last_interaction_id: Optional[int]
    user_name: Optional[str] # Add user_name to AgentState

llm = ChatGroq(
    model="meta-llama/llama-4-maverick-17b-128e-instruct", #meta-llama/llama-4-maverick-17b-128e-instruct  llama-3.3-70b-versatile
    temperature=0.4,
)

# Tools list, now also used by the extraction_node
tools = [log_interaction, edit_interaction, search_hcp, suggest_follow_up, generate_summary, check_compliance, set_user_name, extract_interaction_data]
llm_with_tools = llm.bind_tools(tools)

# Prompt for the LLM's general conversational agent
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an intelligent AI assistant for pharmaceutical field representatives.
Your primary goal is to help the user manage HCP interactions.

You can perform the following actions based on user requests:
- Log a new interaction (via the `log_interaction` tool, but only AFTER an interaction's data has been extracted by `extract_interaction_data`).
- Edit an existing interaction (via the `edit_interaction` tool).
- Search for HCP details (via the `search_hcp` tool).
- Suggest follow-up actions (via the `suggest_follow_up` tool).
- Generate a summary of interaction notes (via the `generate_summary` tool).
- Remember the user's name (via the `set_user_name` tool).

Always provide clear, friendly, and concise responses.

FYI: The ID of the most recent interaction in the database is {last_interaction_id}. Use this ID if the user refers to "the last one" or a recent interaction without specifying an ID.
{user_greeting}
"""),
    MessagesPlaceholder(variable_name="messages"),
])

# Prompt for the dedicated extraction node
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert at extracting structured data about HCP interactions.
Your ONLY task is to extract details from the user's message into the `extract_interaction_data` tool.
ALWAYS call the `extract_interaction_data` tool with ALL relevant information you can extract.
If the user also provides their name, call the `set_user_name` tool.
Do NOT generate any conversational text. ONLY call tools.
"""),
    MessagesPlaceholder(variable_name="messages"),
])


def extraction_node(state: AgentState):
    """
    This node uses the LLM to call `extract_interaction_data` tool to get structured data from user input.
    It also handles `set_user_name` if the user's name is provided.
    """
    
    # Bind only the extraction tools for this LLM invocation
    extraction_llm = llm.bind_tools([extract_interaction_data, set_user_name])
    
    # Invoke the LLM with the extraction_prompt
    llm_response = extraction_llm.invoke(
        extraction_prompt.format_messages(messages=state["messages"])
    )
    
    extracted_fields = state.get("interaction_data", {}).copy()
    new_messages = [llm_response] # Start with the LLM's response

    # Process tool calls from the LLM's response and execute them
    if isinstance(llm_response, AIMessage) and hasattr(llm_response, "additional_kwargs") and "tool_calls" in llm_response.additional_kwargs:
        for tool_call in llm_response.additional_kwargs["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"]) # Arguments are JSON string
            
            tool_output = None
            if tool_name == "extract_interaction_data":
                tool_output = extract_interaction_data.func(**tool_args)
                if tool_output and "extracted_data" in tool_output:
                    for key, value in tool_output["extracted_data"].items():
                        if value is not None:
                            extracted_fields[key] = value
            elif tool_name == "set_user_name":
                tool_output = set_user_name.func(**tool_args)
                if tool_output and "user_name" in tool_output and tool_output["user_name"] is not None:
                    state["user_name"] = tool_output["user_name"] # Directly update user_name in the state
            
            if tool_output is not None:
                new_messages.append(ToolMessage(content=json.dumps(tool_output), tool_call_id=tool_call["id"])) # Add tool result as ToolMessage
    
    return {
        "messages": new_messages, # Return both LLM response and tool outputs
        "interaction_data": extracted_fields,
        "user_name": state.get("user_name"), # Propagate user_name
    }

def agent_node(state: AgentState):
    """
    This is the main agent node that handles general conversation and tool execution 
    for tasks other than initial data extraction.
    """
    user_greeting = ""
    if state.get("user_name"):
        user_greeting = f"\nRemember, the user's name is {state['user_name']}."
    
    # Invoke the LLM with the full list of tools
    response = llm_with_tools.invoke(
        agent_prompt.format_messages(
            messages=state["messages"],
            last_interaction_id=state.get("last_interaction_id", "not available"),
            user_greeting=user_greeting,
        )
    )
    
    return {
        "messages": [response],
        "interaction_data": state.get("interaction_data", {}), # Preserve interaction_data
        "user_name": state.get("user_name"), # Propagate user_name
    }


def generate_summary_node(state: AgentState):
    interaction_data = state["interaction_data"]
    raw_user_input = state.get("raw_user_input", "") # Use raw user input for summary generation

    if not interaction_data.get("summary"): # If summary is missing, generate it
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

        generated_summary = generate_summary.func(raw_text=summary_raw_text)
        
        interaction_data["summary"] = generated_summary.replace("Summary: ", "")
    
    return {"interaction_data": interaction_data}

def compliance_node(state: AgentState):
    interaction_data = state["interaction_data"]
    topics = interaction_data.get("topics", "")

    compliance_output = check_compliance.func(topics=topics)
    
    interaction_data["compliance_result"] = compliance_output["compliance_message"]

    return {"interaction_data": interaction_data}


workflow = StateGraph(AgentState)

# Add nodes to the workflow
workflow.add_node("extraction_node", extraction_node) # First, always try to extract data
workflow.add_node("generate_summary_node", generate_summary_node)
workflow.add_node("compliance_node", compliance_node)
workflow.add_node("agent_node", agent_node) # The general agent for conversational responses
workflow.add_node("tools", ToolNode(tools)) # Node to execute tools called by agent_node


workflow.set_entry_point("extraction_node") # The very first step is data extraction

# Define the workflow edges
# From extraction node, go to summary generation if needed, else to compliance check
workflow.add_conditional_edges(
    "extraction_node",
    lambda state: "generate_summary_node" if not state["interaction_data"].get("summary") else "compliance_node",
    {"generate_summary_node": "generate_summary_node", "compliance_node": "compliance_node"}
)

workflow.add_edge("generate_summary_node", "compliance_node")
workflow.add_edge("compliance_node", "agent_node") # After compliance, agent provides final response

# The agent_node can decide to call tools (like log_interaction, edit_interaction, search_hcp)
workflow.add_conditional_edges(
    "agent_node",
    tools_condition, # Use the prebuilt tools_condition to check for tool calls
    {"tools": "tools", END: END} # If tools are called, go to tools node, else END
)

workflow.add_edge("tools", END) # After executing tools, the graph ends

graph = workflow.compile()