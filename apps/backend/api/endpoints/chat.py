import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set. Please set it in the backend environment.")
    
    try:
        client = genai.Client(api_key=api_key)
        
        system_instruction = "You are an expert on infectious diseases, outbreaks, epidemiology, and public health. You provide accurate, helpful, and concise answers to questions about diseases and outbreaks."
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=request.message,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
            )
        )
        
        if response.text is not None:
            return ChatResponse(reply=response.text)
        else:
            return ChatResponse(reply="I'm sorry, I couldn't generate a response.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
