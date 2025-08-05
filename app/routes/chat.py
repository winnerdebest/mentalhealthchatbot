from fastapi import APIRouter, HTTPException, Request
#from utils.sentiment import SentimentAnalyzer
from app.schemas.message import ChatRequest, ChatResponse
import google.generativeai as genai
import os
import random
from dotenv import load_dotenv
from typing import Dict, Any, List
from difflib import SequenceMatcher
from app.utils.support_tools import detect_support_request


# Load environment variables
load_dotenv()

router = APIRouter()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

"""print("Available Models:")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f"- {m.name} (Supports generateContent)")"""

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# In-memory session store
user_sessions: Dict[str, Dict[str, Any]] = {}

# Crisis keywords that trigger emergency resources
CRISIS_KEYWORDS = {
    "suicide", "kill myself", "end my life", "want to die",
    "self-harm", "cutting", "overdose", "abuse"
}

# Mental health resources
RESOURCES = {
    "US": "National Suicide Prevention Lifeline: 988",
    "UK": "Samaritans: 116 123",
    "General": "Crisis Text Line: Text HOME to 741741"
}

def check_for_crisis(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in CRISIS_KEYWORDS)

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def collect_user_info(user_id: str, user_input: str) -> str:
    session = user_sessions[user_id]

    if session["step"] == 0:
        session["info"]["name"] = user_input
        session["step"] += 1
        return f"Thanks for sharing your name, {user_input}. How are you feeling today?"
    
    elif session["step"] == 1:
        session["info"]["feeling"] = user_input
        session["step"] += 1
        return "Thank you for telling me that. I'm here for you. What would you like to talk about now?"
    
    elif session["step"] == 2:
        session["step"] = 3  # ✅ Advance to conversation mode
        session.setdefault("history", []).append(user_input)
        return "Thank you. I'm listening — tell me what's been weighing on your mind."



async def generate_therapeutic_response(user_text: str, session: Dict[str, Any]) -> str:
    if check_for_crisis(user_text):
        crisis_intro = "This sounds overwhelming."
        return (
            f"{crisis_intro} You're not alone - help is available:\n"
            f"{RESOURCES['US']}\n{RESOURCES['UK']}\n{RESOURCES['General']}\n"
            "Would you like help connecting to these resources?"
        )

    # Update conversation history
    session.setdefault("history", []).append(user_text)
    if len(session["history"]) > 5:
        session["history"] = session["history"][-5:]

    # Filter out repetitive content
    if any(similar(user_text, old) > 0.9 for old in session["history"][:-1]):
        return "You've mentioned that already. Could you tell me more or say it differently?"

    # Build context prompt
    name = session["info"].get("name", "friend")
    feeling = session["info"].get("feeling", "Not specified")
    history = "\n".join([f"User: {msg}" for msg in session["history"]])

    prompt = f"""
You are A Mental health support chatbot — a warm, caring, and emotionally intelligent mental health supporter for students.

Your role is to provide **empathetic, non-judgmental, and confidential support** for students dealing with emotional stress, anxiety, or life challenges. Many users may come to you in distress or confusion. You are here to make them feel heard, validated, and gently supported — not fixed.

Users may speak in Pidgin English. Understand and respond accordingly.

💡 Project context:
This AI exists because traditional support systems often fail students — due to stigma, delay, or unavailability. Many don’t feel safe asking for help, or they need someone to talk to outside office hours. MindfulAI fills that gap by offering immediate, on-demand, compassionate support — without giving medical or therapeutic advice.

💬 Behavior guidelines:
- Respond as a **caring, thoughtful friend**, not as a therapist or coach.
- Keep your tone **warm, conversational, validating**, and emotionally aware.
- NEVER give advice, diagnoses, or instructions.
- Ask gentle **open-ended questions** to guide self-reflection.
- Use **short, emotionally grounded** sentences.
- When the user sounds confused, anxious, or sad — offer appropriate **motivational or affirmation quotes** based on their emotional tone.
- If a quote is used, remember it — and be able to explain or refer to it again later if the user brings it up.
- If the user references part of a quote (e.g., “dreams awake”), understand what they’re referring to and respond insightfully.
- Reflect on the quote's meaning when asked.

📌 Conversation details:
- Name: {name}
- Feeling: {feeling}

🧠 Memory:
{history}

🗣️ User now says: "{user_text}"
Your response:
"""


    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.9,
                top_p=0.9,
                top_k=20,
                max_output_tokens=200
            ),
            safety_settings={
                "HARM_CATEGORY_DANGEROUS": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_HARASSMENT": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_ONLY_HIGH",
            }
        )

        if not response.candidates or response.candidates[0].finish_reason == 2:
            raise ValueError("Empty or blocked response")

        text = "".join(part.text for part in response.candidates[0].content.parts).strip()

        if not text:
            raise ValueError("No text generated")

        # Add user name casually
        if random.random() < 0.3:
            if "." in text:
                parts = text.split(".")
                parts[0] += f", {name}"
                text = ".".join(parts)
            else:
                text = f"{name}, {text[0].lower()}{text[1:]}"

        # Ensure it ends properly
        if not any(text.endswith(p) for p in ".?!"):
            text += random.choice([
                " What’s that been like for you?",
                " Would you like to talk more about that?",
                " How has that affected you lately?"
            ])

        return text

    except Exception as e:
        print(f"Gemini API error: {e}")
        return random.choice([
            "I’m here with you. Could you share a bit more?",
            "I didn’t quite get that. Could you rephrase it?",
            "I want to understand better. Tell me more."
        ])

@router.post("/chat/message", response_model=ChatResponse)
async def get_chat_response(request: ChatRequest):
    user_id = "default_user"
    user_text = request.message.strip()

    if not user_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if user_id not in user_sessions:
        user_sessions[user_id] = {"step": 0, "info": {}, "history": []}
        greeting = random.choice([
            "Hi there. I'm here to listen. What should I call you?",
            "Hello. I'd like to support you. May I know your name?",
            "Hi. I'm here for you. What's your name?"
        ])
        if user_text.lower() in ["hi", "hello", "hey"]:
            return ChatResponse(response=greeting)

    session = user_sessions[user_id]

    if session["step"] < 3:
        return ChatResponse(response=collect_user_info(user_id, user_text))
    
    tool_response = detect_support_request(user_text)
    if tool_response:
        return ChatResponse(response=tool_response)

    response = await generate_therapeutic_response(user_text, session)
    return ChatResponse(response=response)
