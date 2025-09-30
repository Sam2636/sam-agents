from langgraph.graph import StateGraph, END
from typing import TypedDict

# Define the state schema using TypedDict
class QAState(TypedDict):
    context: str
    question: str
    answer: str

def build_graph(retriever_agent, summarizer_agent, qa_agent):
    # Initialize graph with TypedDict schema
    graph = StateGraph(QAState)

    # Step 1: Retrieve documents
    def retrieve_step(state: QAState):
        docs = retriever_agent.run(state["question"])
        state["context"] = docs
        return state

    # Step 2: Summarize retrieved context
    def summarize_step(state: QAState):
        summary = summarizer_agent.run(state["context"])
        state["context"] = summary
        return state

    # Step 3: Generate answer
    def qa_step(state: QAState):
        answer = qa_agent.run({
            "context": state["context"],
            "question": state["question"]
        })
        state["answer"] = answer
        return state

    # Add nodes
    graph.add_node("retriever", retrieve_step)
    graph.add_node("summarizer", summarize_step)
    graph.add_node("qa", qa_step)

    # Connect nodes
    graph.add_edge("retriever", "summarizer")
    graph.add_edge("summarizer", "qa")
    graph.add_edge("qa", END)

    # Set entry point
    graph.set_entry_point("retriever")

    return graph
