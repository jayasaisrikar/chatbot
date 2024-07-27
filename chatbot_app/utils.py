# chatbot_app/utils.py
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)

def fetch_and_process_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

def create_vector_store(texts):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(texts, embedding=embeddings)
    return vector_store

def build_query_agent(vector_store):
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt_template = """
    Given the context and the question, provide a conversational answer.
    Context: {context}
    Question: {question}
    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    def query(question):
        docs = vector_store.similarity_search(question)
        context = "\n".join([doc.page_content for doc in docs])
        result = chain({"input_documents": docs, "context": context, "question": question}, return_only_outputs=True)
        return result["output_text"]

    return query