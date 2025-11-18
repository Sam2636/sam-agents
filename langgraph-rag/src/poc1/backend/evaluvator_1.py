import os
from dotenv import load_dotenv
from typing import TypedDict, Literal

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from langgraph.server import create_app  # IMPORTANT

# Load API key
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# -----------------------------
# Graph state
# -----------------------------
class State(TypedDict):
    joke: str
    topic: str
    feedback: str
    funny_or_not: str

# -----------------------------
# Evaluator schema
# -----------------------------
class Feedback(BaseModel):
    grade: Literal["funny", "not funny"]
    feedback: str

evaluator = llm.with_structured_output(Feedback)

# -----------------------------
# Nodes
# -----------------------------
def llm_call_generator(state: State):
    if state.get("feedback"):
        prompt = f"Write a better joke about {state['topic']} using this feedback: {state['feedback']}"
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
    return "Accepted" if state["funny_or_not"] == "funny" else "Rejected + Feedback"

# -----------------------------
# Build Graph
# -----------------------------
builder = StateGraph(State)

builder.add_node("llm_call_generator", llm_call_generator)
builder.add_node("llm_call_evaluator", llm_call_evaluator)

builder.add_edge(START, "llm_call_generator")
builder.add_edge("llm_call_generator", "llm_call_evaluator")

builder.add_conditional_edges(
    "llm_call_evaluator",
    route_joke,
    {
        "Accepted": END,
        "Rejected + Feedback": "llm_call_generator",
    }
)

graph = builder.compile()

# -----------------------------
# Expose graph to LangGraph Studio
# -----------------------------
app = create_app(graph)

