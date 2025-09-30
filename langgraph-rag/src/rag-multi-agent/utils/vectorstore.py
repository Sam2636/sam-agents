from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

# .env is **two levels up from utils**: rag-multi-agent/utils → src → project root
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
print("Loading .env from:", os.path.abspath(dotenv_path))
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
print("API Key:", api_key)  # Should now print your key

def build_vectorstore(docs):
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    return FAISS.from_texts(docs, embeddings)
