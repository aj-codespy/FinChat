import os
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from pypdf import PdfReader
import docx
import streamlit as st

# --- Configuration ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get('GEMINI_API_KEY'))
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_document_text(uploaded_file):
    """Extracts text from an uploaded PDF or DOCX file."""
    text = ""
    if uploaded_file is None:
        return text
    
    file_extension = os.path.splitext(uploaded_file.name)[1]
    
    try:
        if file_extension == '.pdf':
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        elif file_extension == '.docx':
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""
    return text

def get_text_chunks(text):
    """Splits text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    """Creates and saves a vector store from text chunks."""
    if not text_chunks or not GEMINI_API_KEY:
        st.error("Cannot create vector store. Check API key or document content.")
        return
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
    except Exception as e:
        st.error(f"Error creating vector store: {e}")

def summarize_document_map_reduce(text_chunks):
    """
    Generates a comprehensive summary using the Map-Reduce technique.
    """
    if not text_chunks or not GEMINI_API_KEY:
        return "Document is empty, could not be read, or Gemini API key is missing."

    docs = [Document(page_content=t) for t in text_chunks]
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.2)
    
    # Map prompt
    map_template = """
    Below is a section of a financial document:
    "{docs}"
    Based on this, please identify and summarize the key financial results, risks, and strategic initiatives mentioned.
    Helpful Answer:"""
    map_prompt = PromptTemplate.from_template(map_template)
    
    # Reduce prompt
    reduce_template = """
    You have been provided a series of summaries from a financial document.
    "{doc_summaries}"
    Synthesize these into a final, cohesive summary. The summary should be well-organized, highlighting:
    1. Overall financial performance (revenue, profit, key metrics).
    2. Major strategic initiatives or changes.
    3. Noteworthy risks or challenges identified.
    Final Answer:"""
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    
    chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=reduce_prompt,
        return_intermediate_steps=False,
    )
    
    try:
        summary = chain.invoke({"input_documents": docs})
        return summary['output_text']
    except Exception as e:
        return f"Error during Map-Reduce summarization: {e}"

def get_conversational_chain():
    """Creates a question-answering chain with a custom prompt."""
    prompt_template = """
    You are a financial analyst assistant. Answer the question as detailed as possible from the provided context.
    If the answer is not in the provided context, state that clearly. Do not make up information.

    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    """Handles user queries against the document vector store."""
    if not GEMINI_API_KEY:
        return "Gemini API key is not configured."
        
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    try:
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        chain = get_conversational_chain()
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        return response["output_text"]
    except Exception as e:
        return f"Could not query the document. Ensure it was processed correctly. Error: {e}"

