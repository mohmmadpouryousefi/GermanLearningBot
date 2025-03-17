import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your_default_key_here")

async def ask_openrouter(prompt, purpose="general"):
    """
    Send a prompt to OpenRouter API and get a response.
    
    Args:
        prompt (str): The prompt to send to the API
        purpose (str): The purpose of the request (for logging)
        
    Returns:
        str: The text response from the API
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/yourusername/GermanLearningBot",  # Update with your actual GitHub URL
        "X-Title": "German Learning Bot"
    }
    
    data = {
        "model": "openai/gpt-3.5-turbo",  # You can change this to another model if needed
        "messages": [
            {"role": "system", "content": f"You are a German language tutor assistant. Purpose: {purpose}"},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    error_text = await response.text()
                    raise Exception(f"API Error: {response.status} - {error_text}")
    except Exception as e:
        print(f"Error in ask_openrouter: {str(e)}")
        raise