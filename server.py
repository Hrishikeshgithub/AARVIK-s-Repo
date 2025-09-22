from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import uuid
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Initialize embeddings and LLM
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_AI_API_KEY)

# Pydantic models for request/response
class Question(BaseModel):
    session_id: str
    question: str

class SessionResponse(BaseModel):
    session_id: str

# Helper function to process PDF and store embeddings
async def process_pdf(file: UploadFile, session_id: str):
    try:
        pdf_reader = PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            extracted_text = page.extract_text() or ""
            logger.info(f"Extracted text length from page: {len(extracted_text)}")
            text += extracted_text

        if not text.strip():
            logger.error(f"No text extracted from PDF for session {session_id}")
            raise HTTPException(status_code=400, detail="PDF contains no extractable text")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_text(text)
        logger.info(f"Split text into {len(texts)} chunks for session {session_id}")

        vector_store = FAISS.from_texts(texts, embeddings)
        vector_store.save_local(f"faiss_index_{session_id}")
        logger.info(f"Saved FAISS index for session {session_id}")

        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"pdf_processed": True, "pdf_name": file.filename}},
            upsert=True
        )
        logger.info(f"Processed PDF for session {session_id}")
        return True
    except Exception as e:
        logger.error(f"Error processing PDF for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

# Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to AskPDFStreamlit API. Use /api/health to check status."}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session():
    session_id = str(uuid.uuid4())
    await db.sessions.insert_one({"session_id": session_id, "pdf_processed": False})
    logger.info(f"Created session {session_id}")
    return {"session_id": session_id}

@app.post("/api/upload_pdf")
async def upload_pdf(session_id: str, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        logger.error(f"Invalid file format for session {session_id}: {file.filename}")
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    session = await db.sessions.find_one({"session_id": session_id})
    if not session:
        logger.error(f"Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    await process_pdf(file, session_id)
    return {"message": f"PDF uploaded and processed for session {session_id}"}

@app.post("/api/ask_question")
async def ask_question(question: Question):
    session = await db.sessions.find_one({"session_id": question.session_id})
    if not session:
        logger.error(f"Session not found for ask_question: {question.session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.get("pdf_processed", False):
        logger.error(f"No PDF processed for session: {question.session_id}")
        raise HTTPException(status_code=404, detail="No PDF processed for this session")
    
    try:
        index_path = f"faiss_index_{question.session_id}"
        if not os.path.exists(index_path):
            logger.error(f"FAISS index not found at {index_path} for session {question.session_id}")
            raise HTTPException(status_code=404, detail="FAISS index not found")
        
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(),
        )
        response = qa_chain.invoke({"query": question.question})["result"]
        logger.info(f"Answered question for session {question.session_id}: {question.question}")
        return {"answer": response}
    except Exception as e:
        logger.error(f"Error answering question for session {question.session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    result = await db.sessions.delete_one({"session_id": session_id})
    if result.deleted_count == 0:
        logger.error(f"Session not found for deletion: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        import shutil
        shutil.rmtree(f"faiss_index_{session_id}")
        logger.info(f"Deleted FAISS index for session {session_id}")
    except FileNotFoundError:
        logger.warning(f"FAISS index not found for session {session_id}")
    
    logger.info(f"Deleted session {session_id}")
    return {"message": f"Session {session_id} deleted"}

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()