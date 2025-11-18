from typing import TypedDict, Literal, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt, RetryPolicy
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv


load_dotenv()  # Load variables from .env file
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment variables")

# 1. Define the state schema
class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str

class EmailAgentState(TypedDict):
    email_content: str
    sender_email: str
    email_id: str
    classification: EmailClassification | None
    search_results: list[str] | None
    customer_history: dict | None
    draft_response: str | None
    messages: list[str] | None

# 2. Instantiate LLM wit apikey LangChain
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
structured_llm = llm.with_structured_output(EmailClassification, method="function_calling")


# 3. Define nodes
def read_email(state: EmailAgentState) -> dict:
    return {
        "messages": [HumanMessage(content=f"Processing email: {state['email_content']}")]
    }

import json

def classify_intent(state):
    email_text = state["email"]
    print("🔍 Classifying intent for email:", email_text)

    # Call your model
    response = llm.invoke([
        {"role": "system", "content": "You are an email intent classifier."},
        {"role": "user", "content": f"Classify this email: {email_text}"}
    ])

    # Convert to text
    content = response.content if hasattr(response, "content") else str(response)

    # Try parsing JSON output
    try:
        classification = json.loads(content)
    except Exception:
        print("⚠️ Model didn't return JSON, got:", content)
        classification = {"intent": "unknown", "urgency": "normal"}

    # ✅ Ensure keys exist
    classification.setdefault("intent", "unknown")
    classification.setdefault("urgency", "normal")

    # Example routing logic
    if classification["intent"] == "billing" or classification["urgency"] == "critical":
        next_step = "escalate"
    else:
        next_step = "respond"

    return {"classification": classification, "next": next_step}


def search_documentation(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    classification = state.get('classification', {})
    query = f"{classification.get('intent','')} {classification.get('topic','')}"
    # simulate search
    search_results = [
        "Reset password via Settings > Security > Change Password",
        "Password must be at least 12 characters",
        "Include uppercase, lowercase, numbers, and symbols"
    ]
    return Command(update={"search_results": search_results}, goto="draft_response")

def bug_tracking(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    ticket_id = "BUG-12345"
    return Command(
        update={
            "search_results": [f"Bug ticket {ticket_id} created"],
            "current_step": "bug_tracked"
        },
        goto="draft_response"
    )

def draft_response(state: EmailAgentState) -> Command[Literal["human_review", "send_reply"]]:
    classification = state.get('classification', {})
    ctx_sections = []
    if state.get('search_results'):
        docs_formatted = "\n".join([f"- {d}" for d in state['search_results']])
        ctx_sections.append(f"Relevant documentation:\n{docs_formatted}")
    if state.get('customer_history'):
        ctx_sections.append(f"Customer tier: {state['customer_history'].get('tier','standard')}")
    prompt = f"""
    Draft a response to this customer email:
    {state['email_content']}

    Email intent: {classification.get('intent','unknown')}
    Urgency level: {classification.get('urgency','medium')}
    {chr(10).join(ctx_sections)}

    Guidelines:
    - Be professional and helpful
    - Address their specific concern
    - Use the provided documentation when relevant
    """
    response = llm.invoke(prompt)
    needs_review = (classification.get('urgency') in ['high', 'critical'] or classification.get('intent') == 'complex')
    goto = "human_review" if needs_review else "send_reply"
    return Command(update={"draft_response": response.content}, goto=goto)

def human_review(state: EmailAgentState) -> Command[Literal["send_reply", END]]:
    classification = state.get('classification', {})
    human_decision = interrupt({
        "email_id": state.get('email_id',''),
        "original_email": state.get('email_content',''),
        "draft_response": state.get('draft_response',''),
        "urgency": classification.get('urgency'),
        "intent": classification.get('intent'),
        "action": "Please review and approve/edit this response"
    })
    if human_decision.get("approved"):
        return Command(
            update={"draft_response": human_decision.get("edited_response", state.get('draft_response',''))},
            goto="send_reply"
        )
    else:
        return Command(update={}, goto=END)

def send_reply(state: EmailAgentState) -> dict:
    print(f"Sending reply: {state['draft_response'][:100]}...")
    # integrate with email API here
    return {}

# 4. Wire together the graph
workflow = StateGraph(EmailAgentState)
workflow.add_node("read_email", read_email)
workflow.add_node("classify_intent", classify_intent)
workflow.add_node("search_documentation", search_documentation, retry_policy=RetryPolicy(max_attempts=3))
workflow.add_node("bug_tracking", bug_tracking)
workflow.add_node("draft_response", draft_response)
workflow.add_node("human_review", human_review)
workflow.add_node("send_reply", send_reply)
workflow.add_edge(START, "read_email")
workflow.add_edge("read_email", "classify_intent")
workflow.add_edge("send_reply", END)

# 5. Compile and run
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

initial_state: EmailAgentState = {
    "email_content": "I was charged twice for my subscription! This is urgent!",
    "sender_email": "customer@example.com",
    "email_id": "email_123",
    "classification": None,
    "search_results": None,
    "customer_history": None,
    "draft_response": None,
    "messages": []
}
config = {"configurable": {"thread_id": "customer_123"}}
result = app.invoke(initial_state, config)
print(f"Draft ready for review: {result.get('draft_response')[:100]}…")

# once human reviews:
from langgraph.types import Command as Cmd
human_response = Cmd(resume={"approved": True, "edited_response": "We sincerely apologize for the double charge. I've initiated an immediate refund..."})
final_result = app.invoke(human_response, config)
print("Email sent successfully!")
