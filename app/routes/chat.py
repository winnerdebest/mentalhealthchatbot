from fastapi import APIRouter
from app.schemas.message import ChatRequest, ChatResponse
import environ
import requests

# Load environment variables
env = environ.Env()
environ.Env.read_env()

router = APIRouter()

# Hugging Face API setup
HF_API_KEY = env("HF_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

# Hugging Face model URLs
EMOTION_API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
CHAT_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

# In-memory session store
user_sessions = {}

REQUIRED_FIELDS = ["name", "age", "reason"]

def collect_user_info(user_id: str, user_input: str) -> str:
    session = user_sessions[user_id]
    step = session["step"]
    current_field = REQUIRED_FIELDS[step]

    session["info"][current_field] = user_input
    session["step"] += 1

    if session["step"] < len(REQUIRED_FIELDS):
        next_field = REQUIRED_FIELDS[session["step"]]
        return f"Please tell me your {next_field}:"
    else:
        return "Thanks! Let's get started. How can I support you today?"

def generate_response(user_text: str, user_id: str = "default_user") -> str:
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "step": 0,
            "info": {}
        }

    session = user_sessions[user_id]

    if session["step"] < len(REQUIRED_FIELDS):
        if session["step"] == 0 and user_text.lower() in ["hi", "hello", "hey"]:
            return "Hi there! Before we begin, what's your name?"

        return collect_user_info(user_id, user_text)

    # Emotion detection
    emotion = "neutral"
    try:
        emotion_payload = {"inputs": user_text}
        emotion_response = requests.post(EMOTION_API_URL, headers=HEADERS, json=emotion_payload)
        emotion_response.raise_for_status()
        prediction = emotion_response.json()

        if isinstance(prediction, list) and isinstance(prediction[0], list):
            prediction = prediction[0]
        if isinstance(prediction, list) and prediction and isinstance(prediction[0], dict):
            emotion = prediction[0].get("label", "neutral").lower()
    except Exception as e:
        print("Emotion detection error:", e)

    try:
        user_info = session["info"]
        prompt = (
            f"<|system|>You are a caring and emotionally intelligent companion trained to provide support. "
            f"Always respond briefly, empathetically, and ask gentle questions to help users express themselves.\n"
            f"<|user|>The user's name is {user_info['name']}, age {user_info['age']}, here for {user_info['reason']}.\n"
            f"Their current emotion is: {emotion}.\n"
            f"They said: \"{user_text}\"\n"
            f"<|assistant|>"
        )

        chat_payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "repetition_penalty": 1.1
            }
        }

        chat_response = requests.post(CHAT_API_URL, headers=HEADERS, json=chat_payload)
        chat_response.raise_for_status()
        data = chat_response.json()

        if isinstance(data, list) and "generated_text" in data[0]:
            full_text = data[0]["generated_text"]
            generated_text = full_text.split("<|assistant|>")[-1].strip()
        else:
            generated_text = data.get("generated_text", "I'm here if you want to talk more.")

        # Trim to 2 sentences max
        sentences = generated_text.split(".")
        if len(sentences) > 2:
            generated_text = ". ".join(sentences[:2]).strip() + "."

        # Append emotion-aware follow-up
        follow_ups = {
            "sadness": "Do you want to talk about what's been making you feel this way?",
            "anger": "Would you like to share what’s been bothering you lately?",
            "fear": "Is there anything in particular you’re worried about right now?",
            "joy": "That’s wonderful! What’s been bringing you joy recently?",
            "surprise": "That sounds unexpected! Want to talk more about it?",
            "disgust": "That sounds unpleasant — want to tell me more?",
            "neutral": "Would you like to talk about how your day has been so far?"
        }
        follow_up = follow_ups.get(emotion, "")
        if follow_up and not generated_text.endswith("?"):
            generated_text += " " + follow_up

        # Emoji response
        emojis = {
            "joy": "😊", "sadness": "🤗", "anger": "😌", "fear": "🌟",
            "surprise": "😮", "neutral": "💭", "disgust": "💝"
        }
        emoji = emojis.get(emotion, "💭")

        return f"{generated_text} {emoji}"

    except Exception as e:
        print("Text generation error:", e)
        return "I'm having some trouble responding right now. Can you try again later? 🤔"

@router.post("/chat/message", response_model=ChatResponse)
def get_chat_response(request: ChatRequest):
    user_input = request.message
    reply = generate_response(user_input, user_id="default_user")
    return ChatResponse(response=reply)
