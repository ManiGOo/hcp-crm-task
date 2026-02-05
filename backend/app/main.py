from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime # Import datetime

from .agent.graph import graph, AgentState
from .database import get_db
from . import crud, schemas

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json
from dotenv import load_dotenv
import os
import dateparser

load_dotenv()

app = FastAPI(title="Aivoa AI CRM HCP Log Interaction")

# CORS remains open for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_name: Optional[str] = None # Add user_name to ChatRequest

@app.post("/chat")
async def chat_with_agent(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Get the most recent interaction ID to provide context to the agent
        last_interaction = await crud.get_most_recent_interaction(db)
        last_interaction_id = last_interaction.id if last_interaction else None

        # 1. Initialize state with DB session, last interaction ID, and user_name from request
        initial_state = AgentState(
            messages=[HumanMessage(content=request.message)],
            interaction_data={},
            raw_user_input=request.message,
            db_session=db,
            last_interaction_id=last_interaction_id,
            user_name=request.user_name, # Pass user_name from the request to the state
        )

        # 2. Invoke Graph (using standard invoke as per your current graph setup)
        # Note: If your graph/tools are async, use await graph.ainvoke()
        result = graph.invoke(initial_state)

        reply = "No reply generated."
        extracted_data = {}

        # 3. Extract tool output and AI response
        for msg in result["messages"]:
            if isinstance(msg, AIMessage) and msg.content and msg.content.strip():
                reply = msg.content
            elif isinstance(msg, ToolMessage):
                content = msg.content
                # Handle both dict and JSON-string responses from tools
                if isinstance(content, dict):
                    extracted_data = content
                elif isinstance(content, str):
                    try:
                        extracted_data = json.loads(content)
                    except json.JSONDecodeError:
                        pass # Keep current reply if string is just text

        # 4. Persistence Logic for CREATE
        if extracted_data and "hcp_name" in extracted_data:
            try:
                # --- Preprocessing extracted_data for date and time ---
                if "date" in extracted_data:
                    if extracted_data["date"] == "not specified":
                        extracted_data["date"] = None
                    else:
                        # Use dateparser for robust date parsing
                        parsed_date = dateparser.parse(extracted_data["date"])
                        if parsed_date:
                            extracted_data["date"] = parsed_date.strftime('%Y-%m-%d')
                        else:
                            # If parsing fails, set to None to avoid validation errors
                            extracted_data["date"] = None
                
                if "time" in extracted_data and extracted_data["time"] == "not specified":
                    extracted_data["time"] = None
                
                # --- NEW Preprocessing for interaction_type ---
                if "interaction_type" in extracted_data and extracted_data["interaction_type"].lower() == "virtual meeting":
                    extracted_data["interaction_type"] = "Virtual"
                # --- End NEW Preprocessing ---

                # Validation: Pydantic will ensure lowercase enums here
                interaction_in = schemas.InteractionCreate(**extracted_data)
                
                # CRUD: Async save to PostgreSQL
                new_interaction = await crud.create_interaction(db, interaction_in)
                
                reply = f"✅ Interaction for {extracted_data['hcp_name']} saved successfully with ID #{new_interaction.id}!"
            except Exception as db_err:
                print(f"DB Error: {db_err}")
                # We still return the extracted_data so the frontend form can auto-fill
                reply = f"Interaction extracted but failed to save: {str(db_err)}"
        
        # 5. Persistence Logic for EDIT
        elif extracted_data and extracted_data.get("tool_name") == "edit_interaction":
            try:
                interaction_id = extracted_data["interaction_id"]
                updates = extracted_data["updates"]

                # Convert to the Pydantic schema for validation
                update_schema = schemas.InteractionUpdate(**updates)

                # Call the CRUD function to update the database
                updated_interaction = await crud.update_interaction(db, interaction_id, update_schema)

                if updated_interaction:
                    updated_fields = ", ".join(updates.keys()) or "No changes"
                    reply = f"✅ Interaction #{interaction_id} updated successfully! Fields changed: {updated_fields}."
                else:
                    reply = f"❌ Could not find interaction #{interaction_id} to update."

            except Exception as db_err:
                print(f"DB Error on update: {db_err}")
                reply = f"Interaction edit failed to save: {str(db_err)}"

        # 6. Persistence Logic for SEARCH
        elif extracted_data and extracted_data.get("tool_name") == "search_hcp":
            try:
                query = extracted_data["query"]
                found_interactions = await crud.get_interactions_by_hcp_name(db, query)

                if found_interactions:
                    reply_parts = [f"Found {len(found_interactions)} interaction(s) for '{query}':"]
                    for interaction in found_interactions:
                        reply_parts.append(
                            f"- ID: {interaction.id}, HCP: {interaction.hcp_name}, Type: {interaction.interaction_type}, "
                            f"Date: {interaction.date}, Summary: {interaction.summary or 'N/A'}"
                        )
                    reply = "\n".join(reply_parts)
                else:
                    reply = f"❌ No interactions found for '{query}'."
            except Exception as db_err:
                print(f"DB Error on search: {db_err}")
                reply = f"Search for '{query}' failed: {str(db_err)}"

        # 7. Handle Compliance Check Output (from ToolMessage if LLM called it)
        # Note: If the compliance check is a mandatory node, its output might be in result["interaction_data"]
        # So we check both here.
        if "compliance_result" in result["interaction_data"]:
            compliance_message = result["interaction_data"]["compliance_result"]
            # Prepend the compliance message to the reply
            reply = f"{compliance_message}\n{reply}" if reply != "No reply generated." else compliance_message

        # 8. Handle set_user_name tool output
        elif extracted_data and extracted_data.get("tool_name") == "set_user_name":
            user_name = extracted_data["user_name"]
            reply = f"Hello {user_name}! It's nice to meet you. How can I assist you with your HCP interactions today?"
            extracted_data["user_name"] = user_name # Ensure user_name is returned for frontend persistence


        return {
            "reply": reply,
            "extracted_data": extracted_data,
        }

    except Exception as e:
        print("Critical Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/interactions", response_model=list[schemas.Interaction])
async def list_interactions(db: AsyncSession = Depends(get_db)):
    """Retrieve all logged HCP interactions from the database."""
    return await crud.get_interactions(db)
