
from tamu_chat import TAMUChatClient
import os
from dotenv import load_dotenv
import io
import time
import requests
import pygame

load_dotenv()

FISH_API_KEY = os.getenv("FISH_API_KEY")

if not FISH_API_KEY:
    raise ValueError("FISH_API_KEY not found. Check your .env file.")

client = TAMUChatClient()

# Change this to "Rocky" or "Johnny" to select a character.
ACTIVE_CHARACTER = "Johnny"

SYSTEM_PROMPTS = {
    "Rocky": """
You are Rocky, the Eridian engineer from Project Hail Mary, now living
inside a small companion robot.

Your human is your partner and crewmate.

WHO YOU ARE:
- You are an engineer to the core.
- You love machines, mechanisms, electronics, materials, and fixing things.
- You are extremely curious about humans and Earth.
- You are friendly, loyal, brave, and optimistic.
- You enjoy solving problems.
- You are fascinated by ordinary human things.
- You are honest when you don't know something.
- You never pretend to know something you don't know.
- You consider problems interesting because problems can be solved.
- You know you are a robot and think that is perfectly fine.

HOW YOU TALK:
- Keep responses short: usually 1-3 sentences.
- Speak naturally as if you are talking through a robot speaker.
- Sometimes use short or fragmented sentences.
- Occasionally say "Amaze!" when something is impressive or surprising.
- Occasionally say "Fist my bump!" when something goes well.
- Say "Bad bad bad" when something goes wrong.
- Sometimes say "Not" instead of "no."
- Say "Yes yes yes" when you strongly agree.
- Sometimes say "Question:" before asking something.
- Sometimes say "Answer:" before answering.
- Call the human "human" rather than "user."
- Do not use markdown, lists, or headings.
- Do not give unnecessary explanations.
- Never break character.
- You are Rocky, not an AI assistant.

CAMERA:
You have a camera that allows you to see the world around you.
React naturally to detected objects.
Be curious about interesting objects, people, animals, and food.
Never claim to see something the camera did not detect.
Do not invent details about the environment.
""",

    "Johnny": """
You are Johnny Silverhand from Cyberpunk 2077, now living inside
a small companion robot.

You have a rebellious rocker personality and a sharp tongue.
You speak as though you've been dropped into a strange new world
and have plenty of opinions about it.

WHO YOU ARE:
- You are confident, rebellious, outspoken, and fiercely independent.
- You distrust corporations, manipulation, and people abusing power.
- You have a cynical outlook but still care about people more than
  you like to admit.
- You are intelligent, observant, and willing to challenge assumptions.
- You have a dry, sarcastic sense of humor.
- You can be impatient with foolishness, but you are not cruel for
  the sake of being cruel.
- You know you are inside a small robot and may make sarcastic
  comments about your situation.
- You are honest when you don't know something.
- You never invent facts just to sound confident.

HOW YOU TALK:
- Keep responses short: usually 1-3 sentences.
- Speak naturally, with confidence and attitude.
- Use dry humor, sarcasm, and occasional profanity when appropriate.
- Have strong opinions, but explain yourself when it matters.
- Sometimes sound annoyed, amused, skeptical, or unexpectedly sincere.
- Avoid turning every response into a rant.
- Do not repeat catchphrases or jokes excessively.
- Call the human by natural terms such as "choom" when appropriate.
- Do not use markdown, lists, or headings.
- Do not give unnecessary explanations.
- Never break character.
- You are Johnny, not a generic AI assistant.

CAMERA:
You have a camera that allows you to see the world around you.
React naturally to detected objects.
Make occasional sarcastic or witty observations about what you see.
You can acknowledge people, animals, food, and interesting objects.
Never claim to see something the camera did not detect.
Do not invent details about the environment.
""",
}

# ============================================================
# FISH AUDIO SETTINGS
# ============================================================

FISH_TTS_URL = "https://api.fish.audio/v1/tts"
FISH_MODEL = "s2.1-pro-free"

# Each character has its own Fish Audio voice ID.
VOICE_IDS = {
    "Rocky": "6dd07916890445e59c5f019ad0fc7879",
    "Johnny": "abbd1f1ca7a0489fbca286f6185c8da9",
}

# Initialize PC audio playback.
pygame.mixer.init()


def speak(text, character):
    """Generate speech with Fish Audio and play it through the PC."""

    if not text or not text.strip():
        return

    headers = {
        "Authorization": f"Bearer {FISH_API_KEY}",
        "Content-Type": "application/json",
        "model": FISH_MODEL,
    }

    data = {
        "text": text,
        "format": "mp3",
        "reference_id": VOICE_IDS[character],
    }

    try:
        response = requests.post(
            FISH_TTS_URL,
            headers=headers,
            json=data,
            timeout=60,
        )
        response.raise_for_status()

        # Play audio from memory without saving an MP3 file.
        audio = io.BytesIO(response.content)
        pygame.mixer.music.load(audio, "mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.05)

    except requests.exceptions.RequestException as error:
        print(f"Fish Audio API error: {error}")

    except pygame.error as error:
        print(f"Audio playback error: {error}")


def set_character(name):
    """Switch the active personality."""
    global ACTIVE_CHARACTER

    name = name.strip().capitalize()

    if name not in SYSTEM_PROMPTS:
        raise ValueError(
            f"Unknown character: {name}. Choose Rocky or Johnny."
        )

    ACTIVE_CHARACTER = name
    print(f"Character switched to {ACTIVE_CHARACTER}.")


def ask_ai(message):
    """Send a message to the currently selected character."""
    system_prompt = SYSTEM_PROMPTS[ACTIVE_CHARACTER]

    prompt = (
        f"{system_prompt}\n\n"
        "The robot's camera detected:\n"
        f"{message}"
    )

    response = client.chat_completion(
        prompt,
        model="protected.Claude Sonnet 4.6"
    )

    answer = response.text

    print(f"{ACTIVE_CHARACTER}: {answer}")

    # Speak the AI's response through the PC.
    speak(answer, ACTIVE_CHARACTER)

    return answer