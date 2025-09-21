import os
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from pypdf import PdfReader
import docx
import streamlit as st

# --- Configuration ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get('GEMINI_API_KEY'))
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("[ERROR] Gemini API Key not found for Doc Q&A module.")

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
        print(f"[SUCCESS] Extracted {len(text)} characters from {uploaded_file.name}")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        print(f"[ERROR] Could not read text from file: {e}")
        return ""
    return text

def get_text_chunks(text):
    """Splits text into manageable chunks."""
    print("[INFO] Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    print(f"[SUCCESS] Text split into {len(chunks)} chunks.")
    return chunks

def get_vector_store(text_chunks):
    """Creates and saves a vector store from text chunks."""
    if not text_chunks or not GEMINI_API_KEY:
        st.error("Cannot create vector store. Check API key or document content.")
        return
    try:
        print("[INFO] Creating vector store...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
        print("[SUCCESS] Vector store created and saved to 'faiss_index'.")
    except Exception as e:
        st.error(f"Error creating vector store: {e}")
        print(f"[ERROR] Vector store creation failed: {e}")

def summarize_document_with_full_context(text_chunks):
    """
    Generates a comprehensive summary by sending all chunks to the Gemini model at once.
    This approach leverages the model's large context window.
    """
    print(f"📄 DOC: Starting full-context summary with {len(text_chunks)} chunks")
    if not text_chunks or not GEMINI_API_KEY:
        print(f"❌ DOC: Missing text_chunks or GEMINI_API_KEY")
        return "Document is empty, could not be read, or Gemini API key is missing."

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Combine all text chunks into a single string
        combined_text = "\n\n".join(text_chunks)
        print(f"📝 DOC: Combined text length: {len(combined_text)} characters")
        
        prompt = f"""
        Please analyze the following financial document and provide a comprehensive, well-organized summary. Your summary should highlight:
        1.  **Overall Financial Performance:** Key metrics like revenue, profit, and significant trends.
        2.  **Strategic Initiatives:** Major projects, acquisitions, or changes in business direction.
        3.  **Identified Risks:** Noteworthy risks or challenges mentioned in the document.
        4.  **Outlook & Recommendations:** The company's future outlook and any key recommendations provided.
        
        Document Content:
        ---
        {combined_text}
        ---
        
        Comprehensive Summary:
        """
        
        print(f"🤖 DOC: Generating summary with Gemini...")
        response = model.generate_content(prompt)
        print(f"✅ DOC: Summary generated successfully")
        return response.text
        
    except Exception as e:
        print(f"❌ DOC: Error generating summary: {e}")
        st.error(f"An error occurred during summarization: {e}")
        return f"Error generating summary: {str(e)}"

def user_input(user_question):
    """
    Handles user queries against the document by retrieving relevant chunks and generating an answer.
    """
    print(f"📄 DOC: Answering question: '{user_question}'")
    if not GEMINI_API_KEY:
        return "Gemini API key is not configured."
        
    try:
        # Load the vector store and find relevant documents
        print("    -> Loading FAISS index...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
        db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        print("    -> Searching for relevant chunks...")
        docs = db.similarity_search(user_question, k=5) # Retrieve top 5 relevant chunks
        
        context = "\n\n".join([doc.page_content for doc in docs])
        print(f"    -> Found {len(docs)} relevant chunks to form context.")
        
        # Build the prompt and generate the response
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are a financial analyst assistant. Answer the question as detailed as possible based *only* on the provided context below.
        If the answer is not in the context, state that clearly and do not make up information.

        CONTEXT:
        ---
        {context}
        ---

        QUESTION: {user_question}

        DETAILED ANSWER:
        """
        
        print("    -> Generating answer with Gemini...")
        response = model.generate_content(prompt)
        print("✅ DOC: Answer generated successfully.")
        return response.text
        
    except Exception as e:
        print(f"❌ DOC: Error during user query: {e}")
        st.error(f"An error occurred while querying the document: {e}")
        return f"Could not query the document. Ensure it was processed correctly. Error: {e}"