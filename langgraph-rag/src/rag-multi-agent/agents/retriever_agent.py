from langchain.chains import RetrievalQA

def get_retriever_agent(vectorstore, llm):
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        chain_type="stuff"
    )
