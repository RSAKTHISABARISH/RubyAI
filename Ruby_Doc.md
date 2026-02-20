# Ruby Documentation 

Ruby is a sophisticated, multilingual, semi-humanoid robot assistant designed to support education. It is capable of engaging in natural conversations, performing complex tasks, and providing a visual interface for user interaction. This document provides a deep dive into Ruby's architecture, components, and extensibility.

## Table of Contents
1.  [System Architecture](#system-architecture)
2.  [Core Components](#core-components)
    -   [Ruby Mainframe](#1-ruby-mainframe)
    -   [Frontend Interface](#2-frontend-interface)
3.  [Utilities & Tools](#utilities--tools)
    -   [Speech Services (TTS & STT)](#1-speech-services-tts--stt)
    -   [Integrated Tools](#2-integrated-tools)
    -   [RAG System](#3-rag-system-retrieval-augmented-generation)
4.  [Configuration](#configuration)
5.  [Developer Guide](#developer-guide)

---

## System Architecture

Ruby operates on a modular architecture where a central "brain" (Mainframe) orchestrates interactions between the user, the language model (LLM), and various peripheral tools.

*   **Input**: Audio from the microphone is captured and transcribed by the STT module.
*   **Processing**: The Mainframe processes the text using an OpenAI-powered LangChain agent.
*   **Action**: The agent selects appropriate tools (e.g., YouTube player, Calculator) or generates a conversational response.
*   **Output**: The response is synthesized into speech by the TTS module and displayed effectively on the GUI.

---

## Core Components

### 1. Ruby Mainframe (`ruby/ruby_mainframe.py`)
The `Ruby` class is the heart of the application. It initializes the LangChain agent, manages conversation history, and handles the state loop.

*   **Initialization**: Sets up the LLM (`gpt-4o` by default), tools, system prompt, and speech interfaces.
*   **State Management**: Tracks states like `listening`, `thinking`, `speaking`, and `idle` to update the UI.
*   **Run Loop**: Continuously listens for user input and generates responses.

### 2. Frontend Interface (`frontend/app.py`)
The visual interface is built with **Pygame**, providing real-time feedback on Ruby's status.

*   **Visual Feedback**:
    *   **Blue Pulse**: Listening
    *   **White Pulse**: Thinking / Searching / Playing Video
    *   **Red Pulse**: Speaking
    *   **Grey**: Idle
*   **Interaction**: Users can click the window to immediately stop audio playback.
*   **Threading**: A background thread (`RubyWorker`) handles the blocking AI operations to keep the UI responsive.

---

## Utilities & Tools

### 1. Speech Services (TTS & STT)
Powered by **Google Cloud Platform**.

*   **TTS (`utiles/tts.py`)**:
    *   Converts text response to audio.
    *   Supports multiple Indian languages (English `en-IN`, Malayalam `ml-IN`, Tamil `ta-IN`).
    *   Uses Pygame mixer for playback.
*   **STT (`utiles/stt.py`)**:
    *   Real-time streaming audio recognition.
    *   Handles silence detection and continuous listening.

### 2. Integrated Tools
Ruby is equipped with specific tools to enhance its capabilities (`utiles/ruby_tools.py` & `utiles/toolbox.py`).

*   **`YouTubeVideoPlayerTool`**: Searches and plays educational videos in full screen using `mpv`.
*   **`CalculatorTool`**: safely evaluates mathematical expressions.
*   **`SwitchLanguageTool`**: Dynamically changes the active language for both input and output.
*   **`GetAvailableLanguagesTool`**: Lists supported languages to prevent errors during switching.
*   **`ArduinoSerialCommunication`**: Sends commands to external hardware connected via serial (e.g., `/dev/ttyUSB0`).

### 3. RAG System (Retrieval Augmented Generation)
*   **`query_document`**: A tool that allows Ruby to answer questions based on specific documents loaded into its knowledge base, evaluating queries via the `RubyRAG` class.

---

## Configuration

Ruby is highly configurable via environment variables and direct code adjustments.

### Environment Variables (`.env`)
| Variable | Description |
| :--- | :--- |
| `OPENAI_API_KEY` | Your OpenAI API key for the language model. |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to your Google Cloud JSON service account key. |

### Tool Configuration
*   **Video Player**: Uses `yt-dlp` for extraction and `mpv` for playback. Ensure these are installed on the host system.
*   **Serial Port**: Default is `/dev/ttyUSB0` in `toolbox.py`. Update this to match your hardware setup.

---

## Developer Guide

### Adding a New Tool
1.  Create a function decorated with `@tool` in `utiles/toolbox.py` or a class inheriting `BaseTool` in `utiles/ruby_tools.py`.
2.  Import the tool in `ruby/ruby_mainframe.py`.
3.  Add it to the `self.tools` list in the `Ruby` class `__init__` method.

### Customizing the Persona
Modify `utiles/prompt.py` to change Ruby's personality, rules, or behavior. The system prompt dictates how Ruby introduces itself and responds to multilingual queries.

### Modifying the GUI
Update `frontend/app.py` to change colors, animations, or window dimensions. The `PulseCircle` class controls the central animation.