# Appointment Scheduling Agent with LangGraph + FastAPI
# (empathetic conversation + human-in-the-loop confirmation)

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import TypedDict, Literal
from typing_extensions import Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from fastapi.middleware.cors import CORSMiddleware

# -----------------------------
# Load Environment
# -----------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.7, streaming=True)

# -----------------------------
# Graph State
# -----------------------------
class State(TypedDict):
    user_query: str
    appointment_type: str
    empathetic_reply: str
    appointment_options: str
    user_confirmation: str
    final_status: str

# -----------------------------
# Structured Output for Routing
# -----------------------------
class Intent(BaseModel):
    appointment_type: Literal["doctor", "finance"]
    needs_confirmation: bool

extract_intent = llm.with_structured_output(Intent, method="json_schema", strict=True)

# -----------------------------
# Nodes
# -----------------------------

def empathize_node(state: State):
    reply = llm.invoke(
        f"Respond empathetically to this user's problem and ask one gentle follow-up question: {state['user_query']}"
    )
    return {"empathetic_reply": reply.content}


def classify_intent_node(state: State):
    result = extract_intent.invoke(state["user_query"])
    return {
        "appointment_type": result.appointment_type,
        "user_confirmation": "pending" if result.needs_confirmation else "skip",
    }


def suggest_appointment_node(state: State):
    suggestion = llm.invoke(
        f"Suggest 3 time slots for a {state['appointment_type']} appointment in a warm and caring tone."
    )
    return {"appointment_options": suggestion.content}


def human_confirmation_node(state: State):
    return {
        "empathetic_reply": "Please confirm: Should I book this appointment? (yes/no)",
        "user_confirmation": "awaiting_user",
    }


def finalize_node(state: State):
    if state.get("user_confirmation") == "yes":
        return {"final_status": "Appointment booked successfully!"}
    else:
        return {"final_status": "Okay, I won't book it right now. Let me know if you need anything else."}

# -----------------------------
# Routing
# -----------------------------

def route_after_intent(state: State):
    if state["user_confirmation"] == "pending":
        return "NeedHuman"
    return "Suggest"

# -----------------------------
# Build Graph
# -----------------------------

builder = StateGraph(State)

builder.add_node("Empathize", empathize_node)
builder.add_node("Classify", classify_intent_node)
builder.add_node("Suggest", suggest_appointment_node)
builder.add_node("NeedHuman", human_confirmation_node)
builder.add_node("Finalize", finalize_node)

builder.add_edge(START, "Empathize")
builder.add_edge("Empathize", "Classify")

builder.add_conditional_edges(
    "Classify", route_after_intent, {"NeedHuman": "NeedHuman", "Suggest": "Suggest"}
)

builder.add_edge("NeedHuman", END)  # human must reply manually
builder.add_edge("Suggest", "Finalize")
builder.add_edge("Finalize", END)

workflow = builder.compile()

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="Appointment Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Stream Endpoint
# -----------------------------
@app.get("/appointment/stream")
async def stream(topic: str):
    async def event_gen():
        buffer = ""
        async for event in workflow.astream_events({"user_query": topic}, version="v1"):
            if event["event"] != "on_chat_model_stream":
                continue
            chunk = event["data"]["chunk"].content
            if not chunk:
                continue
            buffer += chunk
            while " " in buffer:
                word, buffer = buffer.split(" ", 1)
                yield f"data: {word} \n\n"
        if buffer:
            yield f"data: {buffer}\n\n"
    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.post("/appointment/confirm")
def confirm(user_confirmation: str):
    result = workflow.invoke({"user_query": "USER", "user_confirmation": user_confirmation})
    return result
