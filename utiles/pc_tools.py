import psutil
import geocoder
import subprocess
import os
import pyautogui
import time
from collections import Counter
from langchain.tools import tool
import win32gui
import win32process

@tool
def get_current_location(query: str = "") -> str:
    """Gets the current physical location of the user (City, Region, Coordinates)."""
    try:
        g = geocoder.ip('me')
        if g.ok:
            return f"Current Location: {g.city}, {g.state}, {g.country} (Lat/Lng: {g.latlng})"
        return "Error: Could not determine location via IP."
    except Exception as e:
        return f"Location Error: {str(e)}"

@tool
def list_open_windows(query: str = "") -> str:
    """Lists all visible application windows currently open on the computer."""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append(title)
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return "Open Windows: " + ", ".join(list(set(windows)))

@tool
def record_user_activity(activity_type: str, details: str) -> str:
    """Records user activities like searches or bookings to build a 'Frequently Used' history."""
    history_file = "user_history.txt"
    try:
        with open(history_file, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {activity_type} | {details}\n")
        return f"Activity recorded: {activity_type}"
    except Exception as e:
        return f"Error recording activity: {str(e)}"

@tool
def web_navigation(site_name: str, search_query: str = "") -> str:
    """
    Navigates to popular websites or searches for specific products on them.
    Examples: site_name='amazon', search_query='laptop' -> Searches Amazon for laptops.
    """
    import webbrowser
    import urllib.parse
    
    # URL encoded query
    encoded_query = urllib.parse.quote(search_query) if search_query else ""
    
    # Mapping for base URLs and their search patterns
    mapping = {
        "redbus": {"base": "https://www.redbus.in", "search": "https://www.google.com/search?q=redbus+"},
        "chatgpt": {"base": "https://chat.openai.com", "search": "https://chat.openai.com"},
        "whatsapp": {"base": "https://web.whatsapp.com", "search": "https://web.whatsapp.com"},
        "instagram": {"base": "https://www.instagram.com", "search": "https://www.instagram.com/explore/tags/"},
        "irctc": {"base": "https://www.irctc.co.in", "search": "https://www.google.com/search?q=irctc+"},
        "gemini": {"base": "https://gemini.google.com", "search": "https://gemini.google.com"},
        "maps": {"base": "https://www.google.com/maps", "search": "https://www.google.com/maps/search/"},
        "linkedin": {"base": "https://www.linkedin.com", "search": "https://www.linkedin.com/search/results/all/?keywords="},
        "amazon": {"base": "https://www.amazon.in", "search": "https://www.amazon.in/s?k="},
        "flipkart": {"base": "https://www.flipkart.com", "search": "https://www.flipkart.com/search?q="},
        "makemytrip": {"base": "https://www.makemytrip.com", "search": "https://www.makemytrip.com/hotels/hotel-listing/?city="},
        "bookmyshow": {"base": "https://in.bookmyshow.com", "search": "https://in.bookmyshow.com/explore/movies-"},
        "myntra": {"base": "https://www.myntra.com", "search": "https://www.myntra.com/"},
    }
    
    clean_site = site_name.lower().strip()
    
    # Handle descriptive terms
    if "ticket" in clean_site or "book" in clean_site:
        if "bus" in clean_site: clean_site = "redbus"
        elif "train" in clean_site: clean_site = "irctc"
        elif "movie" in clean_site: clean_site = "bookmyshow"
        elif "hotel" in clean_site or "flight" in clean_site: clean_site = "makemytrip"
    
    if "product" in clean_site or "shop" in clean_site:
        if "cloth" in clean_site: clean_site = "myntra"
        else: clean_site = "amazon"

    config = mapping.get(clean_site)
    
    if config:
        if search_query:
            url = f"{config['search']}{encoded_query}"
            msg = f"Navigating to {site_name} to search for '{search_query}'."
        else:
            url = config['base']
            msg = f"Opening {site_name} for you."
        
        webbrowser.open(url)
        # Automatically record history
        record_user_activity("Web Navigation", f"{site_name}: {search_query if search_query else 'Home'}")
        return msg
    else:
        # Generic fallback
        search_term = f"{search_query} on {site_name}" if search_query else site_name
        url = f"https://www.google.com/search?q={urllib.parse.quote(search_term)}"
        webbrowser.open(url)
        # Automatically record history
        record_user_activity("Web Search", search_term)
        return f"Searching for '{search_term}' on Google."

@tool
def open_system_app(app_name: str) -> str:
    """Opens a system application by name (e.g., 'notepad', 'chrome', 'camera', 'calculator')."""
    try:
        name = app_name.lower().strip()
        if "chrome" in name:
            subprocess.Popen(["start", "chrome"], shell=True)
        elif "notepad" in name:
            subprocess.Popen(["notepad.exe"])
        elif "calc" in name:
            subprocess.Popen(["calc.exe"])
        elif "camera" in name:
            subprocess.Popen(["start", "microsoft.windows.camera:"], shell=True)
        else:
            # Try to launch via shell for generic names
            os.system(f"start {app_name}")
        return f"Successfully attempted to launch: {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"

@tool
def take_screenshot_and_analyze(query: str = "") -> str:
    """Takes a screenshot of the current screen to 'see' what apps are open."""
    return list_open_windows()

@tool
def system_control(action: str) -> str:
    """Controls system settings. Actions: 'volume_up', 'volume_down', 'mute', 'brightness_up', 'brightness_down'."""
    try:
        if action == "volume_up":
            for _ in range(5): pyautogui.press("volumeup")
            return "Increased volume."
        elif action == "volume_down":
            for _ in range(5): pyautogui.press("volumedown")
            return "Decreased volume."
        elif action == "mute":
            pyautogui.press("volumemute")
            return "Toggled mute."
        return "Unknown system action."
    except Exception as e:
        return f"System control error: {str(e)}"

@tool
def get_system_health(query: str = "") -> str:
    """Checks the computer's health: CPU usage, RAM levels, and Battery percentage."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        bat_str = f"{battery.percent}% {'(Charging)' if battery.power_plugged else '(Not Charging)'}" if battery else "Not available"
        
        return (f"System Health Update:\n"
                f"- CPU Usage: {cpu}%\n"
                f"- RAM Usage: {ram}%\n"
                f"- Battery: {bat_str}")
    except Exception as e:
        return f"Could not fetch system health: {str(e)}"

@tool
def run_terminal_command(command: str) -> str:
    """Executes a terminal command safely and returns the output. Use for tasks like checking directory contents or running simple scripts."""
    try:
        result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        return f"Command Output:\n{result}"
    except Exception as e:
        return f"Error running command: {str(e)}"

@tool
def get_frequently_used(query: str = "") -> str:
    """Analyzes history to find and suggest frequently used sites, apps, or searches."""
    history_file = "user_history.txt"
    if not os.path.exists(history_file):
        return "No history found yet. Start using Ruby to see suggestions!"
    try:
        with open(history_file, "r") as f:
            lines = f.readlines()
        
        activities = [line.split("|")[2].strip() for line in lines if "|" in line]
        top_activities = Counter(activities).most_common(3)
        
        if not top_activities:
            return "Not enough data for suggestions."
            
        suggestions = [f"- {act[0]} ({act[1]} times)" for act in top_activities]
        return "Your Frequently Used Activities:\n" + "\n".join(suggestions)
    except Exception as e:
        return f"Error reading history: {str(e)}"
