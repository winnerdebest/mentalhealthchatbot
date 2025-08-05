import requests
import random
import re

AFFIRMATION_KEYWORDS = {
    "affirmation", "affirm", "encouragement", "encourage", "confidence", 
    "self-esteem", "uplift", "reassure", "positivity", "positive", "worthy", "enough"
}

MOTIVATION_KEYWORDS = {
    "motivate", "motivation", "inspire", "inspiration", "tired", "hopeless", 
    "give up", "burnout", "overwhelmed", "keep going", "determination", "drive", "push", "lost"
}

def clean_text(text):
    return re.sub(r"[^\w\s]", "", text.lower())

def get_affirmation():
    try:
        res = requests.get("https://www.affirmations.dev/")
        if res.ok:
            return res.json().get("affirmation")
    except:
        pass
    return random.choice([
        "You're doing better than you think.",
        "You're enough, just as you are.",
        "Every day is a fresh start.",
        "Your presence is a gift to the world.",
        "You are worthy of love and respect."
    ])

def get_motivation():
    try:
        res = requests.get("https://zenquotes.io/api/random")
        if res.ok:
            quote = res.json()[0]
            return f"{quote['q']} — {quote['a']}"
    except:
        pass
    return random.choice([
        "Keep going. Everything you need will come to you at the perfect time.",
        "Difficult roads often lead to beautiful destinations.",
        "Push yourself, because no one else is going to do it for you.",
        "Success is what comes after you stop making excuses.",
        "You were not born to quit."
    ])

def detect_support_request(text: str) -> str | None:
    cleaned = clean_text(text)

    # Affirmation check
    if any(word in cleaned.split() for word in AFFIRMATION_KEYWORDS):
        return get_affirmation()

    # Motivation check
    if any(word in cleaned.split() for word in MOTIVATION_KEYWORDS):
        return get_motivation()

    # Phrase matching for multi-word expressions
    for phrase in ["give up", "keep going", "burn out", "feel lost"]:
        if phrase in cleaned:
            return get_motivation()

    return None
