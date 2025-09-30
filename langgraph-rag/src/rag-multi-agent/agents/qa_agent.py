from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def get_qa_agent(llm):
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="Answer the question based on the context:\n\nContext: {context}\n\nQuestion: {question}\nAnswer:"
    )
    return LLMChain(llm=llm, prompt=prompt)
