import keyboard
import pyautogui
import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import platform

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in environment variables")

SHORTCUT = os.getenv("SHORTCUT", "alt+y")
MODEL = os.getenv("MODEL", "gemini-2.5-pro-exp-03-25")

PROMPT = """Forget everything before this prompt. Analyze the question in the image and provide ONLY the correct answer, SAY THE TEXT ASSOCIATED TO THE CORRECT ANSWER AND THE QUESTION.
Do not explain your choice or provide any additional context. Return the question followed by "question : " and after a line break "answer : " followed by the correct answer."""

# Configure Gemini
genai.configure(api_key=API_KEY)

def take_screenshot():
    """Takes a screenshot of the active window and returns it as PIL Image."""
    try:
        # Get active window
        active_window = pyautogui.getActiveWindow()
        if active_window is None:
            print("No active window found")
            return None
            
        # Get window coordinates
        left, top = active_window.left, active_window.top
        width, height = active_window.width, active_window.height
        
        # Capture window area
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        return screenshot
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

def send_to_llm(image):
    """Sends the image to Gemini with a prompt."""
    if image is None:
        return None
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content([
            PROMPT,
            {"mime_type": "image/png", "data": image}
        ])
        return {"response": response.text.strip()}
    except Exception as e:
        print(f"Error sending to Gemini: {e}")
        return None

def on_trigger():
    """Function triggered by keyboard shortcut."""
    print("\n" * 3)
    print(datetime.now().strftime("%H:%M:%S"))
    print()
    
    print("Taking screenshot...")
    
    # Take screenshot
    image = take_screenshot()
    if image is None:
        print("Screenshot failed")
        return
    
    # Save locally with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"screenshot_{timestamp}.png"
    try:
        image.save(screenshot_path)
        
        # Convert to bytes for Gemini
        with open(screenshot_path, 'rb') as img_file:
            image_bytes = img_file.read()
        
        # Send to Gemini
        print("Analyzing question...")
        response = send_to_llm(image_bytes)
        
        if response and "response" in response:
            print("\033[94m" + response["response"] + "\033[0m")
        else:
            print("\033[91mFailed to analyze question\033[0m")
            
    except Exception as e:
        print(f"Error processing image: {e}")
    finally:
        # Cleanup
        try:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
        except Exception as e:
            print(f"Error deleting screenshot: {e}")
    
    print("\nWaiting for screenshot... ", end="")

def main():
    """Main function."""
    print(f"Question analysis script started on {platform.system()}")
    print(f"Use {SHORTCUT} to analyze a question")
    print("The script will return the correct answer letter if possible")
    print(f"Model used: {MODEL}")
    
    try:
        keyboard.add_hotkey(SHORTCUT, on_trigger)
        print("\nWaiting for screenshot... ", end="")
        keyboard.wait()
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Script terminated.")

if __name__ == "__main__":
    main()
