from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import sys
import os

# Ensure utils can be imported by adding parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utiles.tts import RubyTTS
from utiles.stt import RubySTT
from utiles.prompt import system_prompt
from utiles.ruby_tools import (
    YouTubeVideoPlayerTool,
    GetAvailableLanguagesTool,
    SwitchLanguageTool,
)
from utiles.toolbox import (
    calculator,
    query_document,
    arduino_serial_communication,
)
from utiles.pc_tools import (
    get_current_location,
    list_open_windows,
    open_system_app,
    system_control,
    web_navigation,
)
load_dotenv()


class Ruby:
    """
    Ruby Mainframe Class.

    This class serves as the central brain of the Ruby assistant. 
    It integrates Speech-to-Text (STT), Text-to-Speech (TTS), and the LangChain 
    agent logic to handle user interactions and tool execution.
    """
    def __init__(self, tts=None, model="gpt-4o", system_prompt=system_prompt, tools=[], stt=None):
        """
        Initialize the Ruby agent.

        Args:
            tts: RubyTTS instance (optional).
            model: Name of the OpenAI model to use (default: "gpt-4o").
            system_prompt: System instructions for the agent.
            tools: List of additional tools.
            stt: RubySTT instance (optional).
        """
        self.model_name = model
        self.ruby_state = "idel"
        self.system_prompt = system_prompt
        
        # Combine default built-in tools with any extra tools provided
        self.tools = [
                        YouTubeVideoPlayerTool(self),   # Tool for playing YouTube videos
                        GetAvailableLanguagesTool(self), # Tool to check supported languages
                        SwitchLanguageTool(self),       # Tool to switch active language
                        calculator,                     # Basic calculator
                        query_document,                 # RAG document query tool
                        arduino_serial_communication,   # Hardware control tool
                        get_current_location,           # Get IP-based location
                        list_open_windows,              # See open apps
                        open_system_app,                # Start apps
                        system_control,                 # Volume/System control
                        web_navigation,                 # Navigate to websites
                    ] + tools

        # Initialize TTS (Text-to-Speech)
        if tts is None:
            self.tts = RubyTTS()
        else:
            self.tts = tts
            
        # Initialize STT (Speech-to-Text)
        if stt is None:
            self.stt = RubySTT()
        else:
            self.stt = stt

        self.system_prompt = system_prompt
        # Initialize conversation history with the system prompt
        self.chat_history = {"messages": [SystemMessage(content=self.system_prompt)]}
        
        # Create the LangChain agent using OpenAI
        self.model = create_agent(
            model=ChatOpenAI(model=self.model_name),
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

    def speak(self, user_input):
        """
        Process user input and generate a response.
        """
        if not user_input:
            return ""

        # FORCE IDENTITY OVERRIDE
        creator_keywords = ["who created you", "who developed you", "who is your creator", "who made you"]
        hod_aiml_keywords = ["who is the hod of aiml", "head of aiml", "hod of ai and ml"]
        
        user_lower = user_input.lower()
        response_text = None

        if any(keyword in user_lower for keyword in creator_keywords):
            response_text = "I was developed by MR. DR. SIVA PRAKASH."
        elif any(keyword in user_lower for keyword in hod_aiml_keywords):
            response_text = "The HOD of AIML is MR. DR. SIVA PRAKASH."

        if response_text:
            self.chat_history["messages"].append(HumanMessage(content=user_input))
            from langchain_core.messages import AIMessage
            self.chat_history["messages"].append(AIMessage(content=response_text))
            
            self.ruby_state = "Speaking"
            self.tts.text_to_speech(response_text)
            self.ruby_state = "idel"
            return response_text

        self.ruby_state = "Thinking"
        self.chat_history["messages"].append(HumanMessage(content=user_input))
        
        # Get response from the agent
        response = self.model.invoke(self.chat_history)
        
        # Add agent's response to history
        self.chat_history["messages"].append(response["messages"][-1])
        
        self.ruby_state = "Speaking"
        # Synthesis speech from the text response
        self.tts.text_to_speech(response["messages"][-1].content)
        
        self.ruby_state = "idel"
        return response["messages"][-1].content
    
    def listen(self):
        """
        Listen for user audio input.
        """
        self.ruby_state = "Listening"
        transcript = self.stt.listen()
        if transcript:
            print(f"User: {transcript}")
        return transcript

    def reset(self):
        """Reset the conversation history to the initial system prompt."""
        self.chat_history = {"messages": [SystemMessage(content=self.system_prompt)]}
        self.ruby_state = "idel"

    def run(self):
        """
        Main loop for console-based interaction.
        Continuously listens and speaks.
        """
        print("--- Ruby is Online ---")
        while True:
            try:
                user_input = self.listen()
                if user_input:
                    self.speak(user_input)
            except KeyboardInterrupt:
                print("\nShutting down Ruby...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")

