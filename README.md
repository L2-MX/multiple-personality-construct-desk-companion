# MPC Desk Companion: Multiple Personality Construct

> A desk companion robot prototype that sees its surroundings with real-time object detection, reasons about what changed using an LLM, and responds out loud as one of several switchable AI personalities.

![Status](https://img.shields.io/badge/status-prototype-orange)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Vision](https://img.shields.io/badge/vision-YOLO11-green)

<!-- Add a photo or GIF of the build here. -->
<!-- ![L2-MX demo](docs/demo.gif) -->

---

## Overview

**MPC** stands for **Multiple Personality Construct**: a single AI companion that can embody many distinct personalities, each with its own character prompt and synthesized voice. This prototype ships with two personas, *Rocky* (the Eridian engineer from *Project Hail Mary*) and *Johnny* (Johnny Silverhand from *Cyberpunk 2077*), and the architecture is designed so more can be added by writing a new prompt and picking a voice.

Under the hood, a webcam feeds a YOLO11 object detector; a filtering layer turns noisy per-frame detections into stable "events" (an object appeared, an object left); an LLM reacts to those events in character; and a text-to-speech engine speaks the reply through the PC.

**Why I built it:** I had used YOLO on a previous project and wanted to go deeper with real-time object detection. After seeing a similar idea used in another project, I set out to build my own version that pairs vision with an LLM and a voice, giving the system a personality instead of just detection output.

---

## Key Features

- **Real-time object detection:** YOLO11n (Ultralytics) runs on the live webcam feed, sampled once per second.
- **Temporal stability filtering:** an object must be seen in 3 consecutive checks before it counts as present, and missing for 3 checks before it counts as gone. This removes flicker and prevents the AI from reacting to false detections.
- **Event-driven AI reactions:** the LLM is only called when the stable scene changes, which keeps API usage and latency low.
- **Short-term memory:** the 5 most recent vision events are passed along as context so responses stay coherent over time.
- **Multiple personality system:** each persona is a system prompt plus a Fish Audio voice ID, so adding a new character takes a few lines. Currently *Rocky* and *Johnny*.
- **Voice output:** responses are synthesized with Fish Audio and played from memory with pygame, with no temporary files written to disk.
- **Grounded responses:** prompts explicitly forbid the character from claiming to see anything the camera didn't detect.

---

## System Architecture

```
           Webcam
             │
             ▼
┌──────────────────────────┐
│ vision.py                │  YOLO11 detection → stability filter
│ (perception)             │  → detects "new" / "removed" objects
└────────────┬─────────────┘
             │ event text
             ▼
┌──────────────────────────┐
│ brain.py                 │  Adds recent-event memory
│ (context)                │  to the current event
└────────────┬─────────────┘
             │ prompt
             ▼
┌──────────────────────────┐
│ ai.py                    │  Character prompt → LLM → reply
│ (personality + voice)    │  → Fish Audio TTS → speakers
└──────────────────────────┘

main.py: entry point
```

| Module | Responsibility |
|---|---|
| `main.py` | Entry point; launches the vision loop |
| `vision.py` | Camera capture, YOLO inference, temporal smoothing, event generation |
| `brain.py` | Combines the current event with recent history and forwards it to the AI layer |
| `ai.py` | Character system prompts, LLM call, and text-to-speech playback |

### How the stability filter works

Raw detectors are noisy: an object can vanish for a single frame or a false positive can appear briefly. To handle this, `vision.py` keeps two counters per object class: how many times it was seen and how many consecutive checks it was missing. An object is promoted to "stable" after 3 sightings and dropped after 3 consecutive misses. Only changes in the stable set generate a message to the AI.

---

## Tech Stack

| Area | Tools |
|---|---|
| Language | Python |
| Computer vision | OpenCV, Ultralytics YOLO11n |
| LLM | Claude Sonnet 4.6 via the TAMU chat client |
| Text-to-speech | Fish Audio API |
| Audio playback | pygame |
| Config | python-dotenv |

---

## Getting Started

### Prerequisites

- Python 3.10 or newer
- A webcam
- A [Fish Audio](https://fish.audio) API key
- Access to the `tamu_chat` client library used for LLM calls

### Installation

```bash
git clone https://github.com/L2-MX/multiple-personality-construct-desk-companion.git
cd multiple-personality-construct-desk-companion
pip install ultralytics opencv-python pygame requests python-dotenv
```

The `yolo11n.pt` weights are downloaded automatically by Ultralytics on first run.

### Configuration

Create a `.env` file in the project root:

```
FISH_API_KEY=your_fish_audio_key_here
TAMU_CHAT_API_KEY=your_tamu_api_key
TAMU_CHAT_BASE_URL=https://chat-api.tamu.ai/openai
```

To choose the active character, edit `ACTIVE_CHARACTER` at the top of `ai.py` (`"Rocky"` or `"Johnny"`), or call `set_character()` at runtime.

### Run

```bash
python main.py
```

A window shows the live camera feed. Press **`q`** to quit.

---

## Example Interaction

Real output from a live run with the Johnny persona:

```
Sending to AI: A new object appeared: person. Currently visible: person.
Johnny: Well, look who decided to show up. You got business with me, or are you just here to stare at a robot?

Sending to AI: A new object appeared: umbrella. Currently visible: person, umbrella.
Johnny: Oh great, company. And what's that, an umbrella? Either it's raining or you're about to do something dramatic.

Sending to AI: A new object appeared: cell phone. An object disappeared: umbrella. Currently visible: person, cell phone.
Johnny: Umbrella's gone and now you're staring at a phone. Let me guess, you put it down to scroll through whatever corporate-owned feed is rotting your brain today.
```

And the same system with the Rocky persona:

```
Rocky: Human! I see you. Also see large flat soft platform. Bed, yes?
Question: is that where humans do the recharge?
```

---

## Project Status

Early prototype with the full perception → reasoning → speech loop working end to end.

**Roadmap**
- [ ] Add speech input so the companion can hear and answer the user
- [ ] Physical enclosure and actuators

---

## What I Learned

- Turning noisy sensor output into reliable events with temporal filtering
- Designing event-driven LLM interactions to control cost and latency
- Prompt engineering for consistent, grounded character personas
- Integrating vision, language, and speech APIs into a single real-time pipeline

