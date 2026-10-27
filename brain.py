
from ai import ask_ai


# Basic objects recognized by YOLO
PEOPLE = [
    "person"
]

ANIMALS = [
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
]

FOOD = [
    "banana",
    "apple",
    "sandwich",
    "orange",
    "pizza",
    "cake",
]


# Send camera messages and recent events to the AI
def think(message, recent_events):
    memory = "Recent events: " + " | ".join(recent_events)
    full_message = memory + "\nCurrent event: " + message

    answer = ask_ai(full_message)
    return answer
