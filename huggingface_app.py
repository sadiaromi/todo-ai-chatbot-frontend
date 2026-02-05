import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

# Add backend to path
sys.path.append('./backend')

# Import backend components
from backend.src.main import app as backend_app_instance
from sqlmodel import SQLModel
from backend.src.services.database import engine

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Set environment variables for Hugging Face Spaces
os.environ.setdefault("DATABASE_URL", "sqlite:///./todo_chatbot_hf.db")

# Set default values for required environment variables
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
os.environ.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "huggingface-spaces-fallback-secret-key"))
os.environ.setdefault("ALGORITHM", os.getenv("ALGORITHM", "HS256"))
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    print("Creating database tables...")
    create_db_and_tables()
    yield
    # Cleanup if needed
    print("Application shutdown")

# Use the backend app instance and add our custom lifespan
backend_app_instance.lifespan = lifespan

# Add a root endpoint for Hugging Face Spaces if it doesn't exist
try:
    @backend_app_instance.get("/")
    def read_root():
        return {"message": "Todo AI Chatbot Backend - Deployed on Hugging Face Spaces"}
except:
    # If the route already exists, we don't need to add it
    pass

# Add health endpoint if it doesn't exist
try:
    @backend_app_instance.get("/health")
    def health_check():
        return {"status": "healthy", "service": "todo-ai-chatbot-backend"}
except:
    # If the route already exists, we don't need to add it
    pass

# Assign the backend app as our main app
app = backend_app_instance

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("huggingface_app:app", host="0.0.0.0", port=port)