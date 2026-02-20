# Ruby Core Agent Tools 

from langchain.tools import BaseTool
from pydantic import PrivateAttr
import subprocess
import yt_dlp


class YouTubeVideoPlayerTool(BaseTool):
    name: str = "youtube_video_player"
    description: str = (
        "Searches YouTube for the given query and selects the top result. "
        "Plays the video in full screen using a lightweight external player. "
        "Blocks execution until the video playback finishes or the player window is closed. "
        "Use this tool only after the user explicitly confirms they want to play a video."
    )


    _ruby = PrivateAttr()
    def __init__(self, ruby):
        super().__init__()
        self._ruby = ruby

    def _run(self, query: str) -> str:
        """
        Args:
            query (str): The search query for the video.
        """
        self._ruby.ruby_state = "Searching Video"
        # Options for yt_dlp to get the video stream url 
        ydl_opts = {
            "quiet": True,
            "default_search": "ytsearch1",
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "skip_download": True,
            "extract_flat": False,
            "js_runtimes": {"node": {}},
            "youtube_include_dash_manifest": False,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            },
            "quiet": True,
            "no_warnings": True,
        }
        import webbrowser
        # Get the video stream url from youtube using yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract the video info from youtube
            info = ydl.extract_info(query, download=False)
            video = info["entries"][0]
            stream_url = video["original_url"]
        
        # Open in default browser
        webbrowser.open(stream_url)
        
        self._ruby.ruby_state = "Playing Video"
        return f"Now playing: {video['title']} in your browser."

class GetAvailableLanguagesTool(BaseTool):
    name: str = "get_available_languages"
    description: str = (
        "Returns a list of all language IDs currently supported by the system's "
        "text-to-speech and speech-to-text engines. "
        "Use this tool before attempting a language switch or when the user asks "
        "which languages are supported."
    )


    _ruby = PrivateAttr()
    def __init__(self, ruby):
        super().__init__()
        self._ruby = ruby

    def _run(self) -> list[str]:
        # Return the list of supported languages
        return self._ruby.tts.get_supported_languages()

class SwitchLanguageTool(BaseTool):
    name: str  = "switch_language"
    description: str = (
        "Switches the assistant's active language for both speech recognition "
        "and speech synthesis. "
        "Input must be a valid language ID obtained from the available languages list. "
        "Do not guess language IDs. "
        "Always verify availability before calling this tool."
    )


    _ruby = PrivateAttr()
    def __init__(self, ruby):
        super().__init__()
        self._ruby = ruby

    def _run(self, language: str) -> str:
        # Update the Ruby state to switching language
        self._ruby.ruby_state = "switching_language"
        # Update the tts and stt language
        self._ruby.tts.update_language(language)
        self._ruby.stt.update_language(language)
        # Update the Ruby state to idle
        self._ruby.ruby_state = "idle"
        return f"Switched to {language}"
