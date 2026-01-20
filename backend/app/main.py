from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime # Import datetime

from .agent.graph import graph, AgentState
from .database import get_db
from . import crud, schemas

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json
from dotenv import load_dotenv
import os

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

@app.post("/chat")
async def chat_with_agent(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        # 1. Initialize state with DB session for tools to use if needed
        initial_state = AgentState(
            messages=[HumanMessage(content=request.message)],
            interaction_data={},
            raw_user_input=request.message, # Ensure raw_user_input is captured
            db_session=db
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

        # 4. Persistence Logic: Save to DB if 'log_interaction' was called
        if extracted_data and "hcp_name" in extracted_data:
            try:
                # --- Preprocessing extracted_data for date and time ---
                if "date" in extracted_data and extracted_data["date"] == "today":
                    extracted_data["date"] = datetime.now().strftime('%Y-%m-%d')
                elif "date" in extracted_data and extracted_data["date"] == "not specified":
                    extracted_data["date"] = None
                
                if "time" in extracted_data and extracted_data["time"] == "not specified":
                    extracted_data["time"] = None
                # --- End Preprocessing ---

                # Validation: Pydantic will ensure lowercase enums here
                interaction_in = schemas.InteractionCreate(**extracted_data)
                
                # CRUD: Async save to PostgreSQL
                await crud.create_interaction(db, interaction_in)
                
                reply = f"✅ Interaction for {extracted_data['hcp_name']} saved successfully!"
            except Exception as db_err:
                print(f"DB Error: {db_err}")
                # We still return the extracted_data so the frontend form can auto-fill
                reply = f"Interaction extracted but failed to save: {str(db_err)}"

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
