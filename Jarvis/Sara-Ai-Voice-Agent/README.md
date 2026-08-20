# Sara — Real-Time AI Voice Agent

A real-time AI voice agent with a lifelike avatar that supports natural voice conversations in **Urdu and English**, answers questions, and understands content shared through the user's screen.

---

## Overview

Sara is a real-time conversational AI agent built with LiveKit. Users can communicate with the agent through voice while interacting with an AI avatar. The agent can answer general questions, switch naturally between Urdu and English, and analyze information shared through the user's screen.

---

## Demo

[![Sara — AI Voice Agent Demo](assets/demo.png)](https://youtu.be/U9D9_PYFu3w)

▶️ **[Watch the demo](https://youtu.be/U9D9_PYFu3w)** — real-time voice conversation with an AI avatar, multilingual interaction, and screen understanding (click the image above to play).

---

## Key Features

**Voice & Conversation**
- Real-time, low-latency voice interaction
- Natural conversational responses
- Urdu and English language support
- Voice-optimized responses for natural text-to-speech

**AI Avatar**
- Real-time AI avatar powered by Bey
- Synchronized voice and avatar experience
- Interactive browser-based experience

**Screen Understanding**
- Real-time screen sharing
- Visual understanding of shared content
- Answers questions based on information visible on the user's screen

---

## Tech Stack

| Area | Technologies |
|------|--------------|
| **Language** | Python |
| **AI / LLM** | Google Gemini Realtime API |
| **Voice / Realtime** | LiveKit Agents, WebRTC |
| **AI Avatar** | Bey Avatar |
| **Backend** | LiveKit Agents |
| **Cloud** | LiveKit Cloud |
| **Async Runtime** | asyncio |
| **Package Management** | uv |

---

## Architecture

```text
User
  │
  ├── 🎤 Voice Input
  └── 🖥️ Screen Share
          │
          ▼
    LiveKit Cloud
          │
          ▼
    LiveKit Agent
          │
     ┌────┴─────┐
     ▼          ▼
 Gemini       Bey Avatar
 Realtime
     │          │
     └────┬─────┘
          ▼
   Voice + Avatar
      Response
