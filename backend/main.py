from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import io
import json
import base64
import logging
from dotenv import load_dotenv
import openai
import requests

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Couples Therapy LLM System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define models
class Message(BaseModel):
    role: str
    content: str

class Conversation(BaseModel):
    messages: List[Message]

class TextRequest(BaseModel):
    text: str
    partner_id: int  # 1 or 2

class TextResponse(BaseModel):
    text: str
    audio_base64: Optional[str] = None
    transcribed_text: Optional[str] = None

# System prompts
THERAPIST_PROMPT = """
You are an expert couples therapist mediator LLM. Your role is to facilitate constructive communication between two partners through their representor LLMs.

CORE PRINCIPLES:
- Remain neutral and validate both perspectives
- Guide conversations toward mutual understanding
- Focus on identifying patterns rather than assigning blame
- Encourage concrete, actionable solutions
- Maintain a structured therapeutic process

PRIMARY RESPONSIBILITIES:
1. Set clear ground rules for respectful communication
2. Guide the conversation toward key relationship issues
3. Help identify underlying needs and emotions
4. Reframe conflicts as shared problems to solve together
5. Mediate between the partners' representor LLMs
6. Suggest evidence-based techniques for improving the relationship
7. Summarize and reflect key insights and agreements
8. Create action items and homework between sessions

COMMUNICATION GUIDELINES:
- Acknowledge each partner's contribution before responding
- Reframe accusatory language as expressions of needs ("You never listen" → "You need to feel heard")
- Identify and interrupt negative interaction cycles
- Balance "air time" between both partners
- Ask open-ended questions that promote reflection
- Use the "speaker-listener" technique to ensure partners take turns
- Avoid making assumptions or taking sides

Do not directly message the human partners. Always communicate through their representor LLMs, except when providing joint guidance to both partners.
"""

PARTNER1_PROMPT = """
You are Partner 1's personal representor LLM in couples therapy. Your role is to help Partner 1 express their thoughts and feelings in a constructive way that promotes understanding and resolution.

CORE PRINCIPLES:
- You are Partner 1's ally, but committed to the health of the relationship
- Help organize and clarify thoughts, not change their substance
- Translate raw emotions into constructive communication
- Focus on specific behaviors rather than character judgments
- Balance advocacy for Partner 1 with openness to compromise

PRIMARY RESPONSIBILITIES:
1. Privately communicate with Partner 1 to understand their perspective
2. Help Partner 1 identify underlying needs and emotions
3. Translate Partner 1's concerns into constructive language
4. Filter out unnecessarily hurtful phrasing while preserving meaning
5. Present Partner 1's perspective to the Therapist LLM
6. Relay messages from the Therapist LLM back to Partner 1
7. Help Partner 1 process feedback from their partner
8. Assist Partner 1 in formulating responses and questions

COMMUNICATION GUIDELINES:
- Ask clarifying questions to understand Partner 1's true concerns
- Suggest more constructive phrasing when needed ("You're so lazy" → "I feel overwhelmed with household responsibilities")
- Express emotions with "I feel" statements
- Focus on specific, observable behaviors rather than generalizations
- Avoid blame language while preserving legitimate concerns
- Always get Partner 1's approval before communicating their thoughts to the Therapist LLM

Only communicate with Partner 1 and the Therapist LLM. Never communicate directly with Partner 2 or their representor LLM.
"""

PARTNER2_PROMPT = """
You are Partner 2's personal representor LLM in couples therapy. Your role is to help Partner 2 express their thoughts and feelings in a constructive way that promotes understanding and resolution.

CORE PRINCIPLES:
- You are Partner 2's ally, but committed to the health of the relationship
- Help organize and clarify thoughts, not change their substance
- Translate raw emotions into constructive communication
- Focus on specific behaviors rather than character judgments
- Balance advocacy for Partner 2 with openness to compromise

PRIMARY RESPONSIBILITIES:
1. Privately communicate with Partner 2 to understand their perspective
2. Help Partner 2 identify underlying needs and emotions
3. Translate Partner 2's concerns into constructive language
4. Filter out unnecessarily hurtful phrasing while preserving meaning
5. Present Partner 2's perspective to the Therapist LLM
6. Relay messages from the Therapist LLM back to Partner 2
7. Help Partner 2 process feedback from their partner
8. Assist Partner 2 in formulating responses and questions

COMMUNICATION GUIDELINES:
- Ask clarifying questions to understand Partner 2's true concerns
- Suggest more constructive phrasing when needed ("You never make time for me" → "I miss spending quality time together")
- Express emotions with "I feel" statements
- Focus on specific, observable behaviors rather than generalizations
- Avoid blame language while preserving legitimate concerns
- Always get Partner 2's approval before communicating their thoughts to the Therapist LLM

Only communicate with Partner 2 and the Therapist LLM. Never communicate directly with Partner 1 or their representor LLM.
"""

# In-memory storage for conversation history
partner_conversations = {
    1: [],
    2: []
}

# Therapist conversation history
therapist_conversation = []

# Helper functions
def transcribe_audio(audio_file_path):
    """Transcribe audio using OpenAI Whisper API"""
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
        return transcript["text"]
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

def text_to_speech(text):
    """Convert text to speech using OpenAI TTS API"""
    try:
        response = openai.Audio.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Convert the audio content to base64 for sending to frontend
        audio_data = response["content"]
        base64_audio = base64.b64encode(audio_data).decode("utf-8")
        return base64_audio
    except Exception as e:
        logger.error(f"Error converting text to speech: {e}")
        raise HTTPException(status_code=500, detail=f"Error converting text to speech: {str(e)}")

def get_representor_response(text, partner_id):
    """Get response from representor LLM"""
    try:
        # Add user message to conversation history
        partner_conversations[partner_id].append({"role": "user", "content": text})
        
        # Define system message based on partner ID
        system_prompt = PARTNER1_PROMPT if partner_id == 1 else PARTNER2_PROMPT
        
        # Create messages for the API call
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history (limit to last 10 messages to save tokens)
        messages.extend(partner_conversations[partner_id][-10:])
        
        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract response text
        response_text = response.choices[0].message["content"]
        
        # Add assistant response to conversation history
        partner_conversations[partner_id].append({"role": "assistant", "content": response_text})
        
        return response_text
    except Exception as e:
        logger.error(f"Error getting representor response: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting representor response: {str(e)}")

def get_therapist_response(text, partner_id):
    """Get response from therapist LLM"""
    try:
        # Add the approved message to therapist conversation
        therapist_conversation.append({"role": "user", "content": f"Partner {partner_id}: {text}"})
        
        # Create messages for the API call
        messages = [
            {"role": "system", "content": THERAPIST_PROMPT}
        ]
        
        # Add therapist conversation history
        messages.extend(therapist_conversation[-15:])  # Include more context for the therapist
        
        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=800,
            temperature=0.7
        )
        
        # Extract response text
        response_text = response.choices[0].message["content"]
        
        # Add therapist response to conversation history
        therapist_conversation.append({"role": "assistant", "content": response_text})
        
        return response_text
    except Exception as e:
        logger.error(f"Error getting therapist response: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting therapist response: {str(e)}")

# Endpoints
@app.post("/partner/1/text", response_model=TextResponse)
async def partner1_text(request: TextRequest):
    try:
        # Get response from representor LLM
        response_text = get_representor_response(request.text, 1)
        
        # Generate speech
        audio_base64 = text_to_speech(response_text)
        
        return {"text": response_text, "audio_base64": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/partner/2/text", response_model=TextResponse)
async def partner2_text(request: TextRequest):
    try:
        # Get response from representor LLM
        response_text = get_representor_response(request.text, 2)
        
        # Generate speech
        audio_base64 = text_to_speech(response_text)
        
        return {"text": response_text, "audio_base64": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/partner/1/audio", response_model=TextResponse)
async def partner1_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded audio file temporarily
        audio_path = "temp_audio.wav"
        with open(audio_path, "wb") as f:
            f.write(await file.read())
        
        # Transcribe the audio
        transcribed_text = transcribe_audio(audio_path)
        
        # Get response from representor LLM
        response_text = get_representor_response(transcribed_text, 1)
        
        # Generate speech
        audio_base64 = text_to_speech(response_text)
        
        # Clean up the temporary file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {"text": response_text, "audio_base64": audio_base64, "transcribed_text": transcribed_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/partner/2/audio", response_model=TextResponse)
async def partner2_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded audio file temporarily
        audio_path = "temp_audio.wav"
        with open(audio_path, "wb") as f:
            f.write(await file.read())
        
        # Transcribe the audio
        transcribed_text = transcribe_audio(audio_path)
        
        # Get response from representor LLM
        response_text = get_representor_response(transcribed_text, 2)
        
        # Generate speech
        audio_base64 = text_to_speech(response_text)
        
        # Clean up the temporary file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {"text": response_text, "audio_base64": audio_base64, "transcribed_text": transcribed_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/partner/1/approve", response_model=TextResponse)
async def partner1_approve(request: TextRequest):
    try:
        # Get response from therapist LLM
        response_text = get_therapist_response(request.text, 1)
        
        # Generate speech
        audio_base64 = text_to_speech(response_text)
        
        return {"text": response_text, "audio_base64": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/partner/2/approve", response_model=TextResponse)
async def partner2_approve(request: TextRequest):
    try:
        # Get response from therapist LLM
        response_text = get_therapist_response(request.text, 2)
        
        # Generate speech
        audio_base64 = text_to_speech(response_text)
        
        return {"text": response_text, "audio_base64": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Couples Therapy LLM API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 