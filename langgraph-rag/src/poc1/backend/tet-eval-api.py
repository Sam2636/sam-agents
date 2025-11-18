import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from typing import TypedDict, Literal
from typing_extensions import Annotated

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END

# -----------------------------
# Environment
# -----------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=api_key,
    streaming=True
)

# -----------------------------
# Graph State
# -----------------------------
class State(TypedDict):
    joke: str
    topic: str
    feedback: str
    funny_or_not: str

# -----------------------------
# Schema for Evaluator
# -----------------------------
class Feedback(BaseModel):
    grade: Literal["funny", "not funny"]
    feedback: str

evaluator = llm.with_structured_output(Feedback,
                                           method="json_schema",strict=True     )

# -----------------------------
# Nodes
# -----------------------------
def llm_call_generator(state: State):
    if state.get("feedback"):
        prompt = f"Write a better joke about {state['topic']}. Improve using this feedback: {state['feedback']}"
    else:
        prompt = f"Write a joke about {state['topic']}"
    msg = llm.invoke(prompt)
    return {"joke": msg.content}

def llm_call_evaluator(state: State):
    grade = evaluator.invoke(f"Grade this joke: {state['joke']}")
    return {
        "funny_or_not": grade.grade,
        "feedback": grade.feedback
    }

def route_joke(state: State):
    if state["funny_or_not"] == "funny":
        return "Accepted"
    else:
        return "Rejected + Feedback"

# -----------------------------
# Build Graph
# -----------------------------
builder = StateGraph(State)

builder.add_node("generate", llm_call_generator)
builder.add_node("evaluate", llm_call_evaluator)

builder.add_edge(START, "generate")
builder.add_edge("generate", "evaluate")

builder.add_conditional_edges(
    "evaluate",
    route_joke,
    {
        "Accepted": END,
        "Rejected + Feedback": "generate"
    },
)

workflow = builder.compile()

# -----------------------------
# FastAPI App
# -----------------------------
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="Joke Stream API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------------------
# Stream Endpoint
# -----------------------------
@app.get("/joke/stream")
async def stream_joke(topic: str):

    async def event_generator():
        buffer = ""

        async for event in workflow.astream_events({"topic": topic}, version="v1"):
            if event["event"] != "on_chat_model_stream":
                continue

            chunk = event["data"]["chunk"].content
            if not chunk:
                continue

            buffer += chunk

            # If we have one or more full words (space separated)
            while " " in buffer:
                word, buffer = buffer.split(" ", 1)
                yield f"data: {word} \n\n"

        # Flush leftover last word
        if buffer:
            yield f"data: {buffer}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# -----------------------------
# Simple Final Joke Endpoint
# -----------------------------
@app.get("/joke/final")
def final_joke(topic: str):
    result = workflow.invoke({"topic": topic})
    return {"final_joke": result["joke"]}
