from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def get_summarizer_agent(llm):
    prompt = PromptTemplate(
        input_variables=["context"],
        template="Summarize the following information:\n\n{context}"
    )
    return LLMChain(llm=llm, prompt=prompt)
