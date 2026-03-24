from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load the secret API key
load_dotenv()
API_KEY = os.getenv("MEMBRAIN_API_KEY")

# Replace these with the actual URLs from the Membrain Docs!
MEMBRAIN_ADD_URL = "https://mem-brain-api-cutover-v4-production.up.railway.app/api/v1/memories" 
MEMBRAIN_SEARCH_URL = "https://mem-brain-api-cutover-v4-production.up.railway.app/api/v1/memories/search"

app = FastAPI()

class StudyNote(BaseModel):
    topic: str
    content: str

class SearchQuery(BaseModel):
    question: str

@app.post("/memorize/")
def memorize_concept(note: StudyNote):
    """Sends a study note to the Membrain API to be stored in the graph."""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "content": f"Topic: {note.topic}. Content: {note.content}",
        "metadata": {"type": "exam_prep", "decay_active": True}
    }
    
    response = requests.post(MEMBRAIN_ADD_URL, headers=headers, json=payload)
    
    if response.status_code in [200, 202]:
        return {"status": "Success! Concept added to Synapse.", "data": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to reach Membrain")

@app.get("/")
def root():
    return {"status": "running", "message": "API is alive. Use /docs for API docs, /memorize/ to add notes, /recall/ to query."}

@app.post("/recall/")
def recall_concept(query: SearchQuery):
    """Searches the Membrain API for an answer based on your stored notes."""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"query": query.question}
    
    response = requests.post(MEMBRAIN_SEARCH_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return {"status": "Recall successful.", "answer": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail="Search failed")
