from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chatbot import Chatbot
import uvicorn
import os

app = FastAPI(title="Haravan AI Chatbot API")

# Initialize Chatbot
try:
    bot = Chatbot()
except Exception as e:
    print(f"Failed to initialize chatbot: {e}")
    bot = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Haravan AI Chatbot is running"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not bot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized properly")
    
    try:
        response_text = bot.process_message(request.message)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
