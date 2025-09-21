import os
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
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
        # Pass the API key directly to the embeddings model
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
    except Exception as e:
        st.error(f"Error creating vector store: {e}")

def summarize_document_map_reduce(text_chunks):
    """
    Generates a comprehensive summary using a simplified approach.
    """
    print(f"📄 DOC: Starting summarize_document_map_reduce with {len(text_chunks)} chunks")
    
    if not text_chunks or not GEMINI_API_KEY:
        print(f"❌ DOC: Missing text_chunks or GEMINI_API_KEY")
        return "Document is empty, could not be read, or Gemini API key is missing."

    try:
        # Configure Gemini
        print(f"🤖 DOC: Configuring Gemini API")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        # Combine all text chunks
        combined_text = "\n\n".join(text_chunks)
        print(f"📝 DOC: Combined text length: {len(combined_text)} characters")
        
        # Create a comprehensive prompt
        prompt = f"""
        Please analyze the following financial document and provide a comprehensive summary.
        
        Document Content:
        {combined_text}
        
        Please provide a well-organized summary highlighting:
        1. Overall financial performance (revenue, profit, key metrics)
        2. Major strategic initiatives or changes
        3. Noteworthy risks or challenges identified
        4. Key business insights and recommendations
        
        Summary:
        """
        
        # Generate summary
        print(f"🤖 DOC: Generating summary with Gemini")
        response = model.generate_content(prompt)
        print(f"✅ DOC: Summary generated successfully")
        return response.text
        
    except Exception as e:
        print(f"❌ DOC: Error generating summary: {e}")
        return f"Error generating summary: {str(e)}"

def get_conversational_chain():
    """Creates a question-answering chain with a custom prompt."""
    if not GEMINI_API_KEY:
        return None
    
    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        return model
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return None

def user_input(user_question):
    """Handles user queries against the document vector store."""
    if not GEMINI_API_KEY:
        return "Gemini API key is not configured."
        
    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        # Load vector store and get relevant documents
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        
        # Combine context from relevant documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create prompt
        prompt = f"""
        You are a financial analyst assistant. Answer the question as detailed as possible from the provided context.
        If the answer is not in the provided context, state that clearly. Do not make up information.

        Context:
        {context}

        Question: {user_question}

        Answer:
        """
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Could not query the document. Ensure it was processed correctly. Error: {e}"

