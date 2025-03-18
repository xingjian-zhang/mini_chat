"""API communication layer for the terminal chatbot."""
import os
import json
import requests
from typing import Dict, List, Any, Optional, Generator, Callable
from requests.exceptions import RequestException

from models import Conversation
from config import get_api_key, load_config

class APIError(Exception):
    """Exception raised for API errors."""
    pass

def send_message(conversation: Conversation, 
                on_content: Optional[Callable[[str], None]] = None) -> str:
    """
    Send conversation to API and get response.
    
    Args:
        conversation: The conversation to send
        on_content: Optional callback for streaming content
        
    Returns:
        The assistant's response text
    
    Raises:
        APIError: If API request fails
    """
    config = load_config()
    api_key = get_api_key()
    
    if not api_key:
        raise APIError("API key not found. Please set the API_KEY environment variable.")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": config["model"],
        "messages": conversation.to_api_format(),
        "max_tokens": config["max_tokens"],
        "temperature": config["temperature"],
        "stream": bool(on_content),  # Stream if callback is provided
    }
    
    try:
        if on_content:
            return _stream_response(headers, data, config["api_base_url"], on_content)
        else:
            return _send_request(headers, data, config["api_base_url"])
    except RequestException as e:
        raise APIError(f"API request failed: {str(e)}")

def _send_request(headers: Dict[str, str], data: Dict[str, Any], base_url: str) -> str:
    """Send a non-streaming request to the API."""
    url = f"{base_url}/chat/completions"
    response = requests.post(url, headers=headers, json=data, timeout=30)
    
    if response.status_code != 200:
        raise APIError(f"API returned error {response.status_code}: {response.text}")
    
    result = response.json()
    return result["choices"][0]["message"]["content"]

def _stream_response(headers: Dict[str, str], data: Dict[str, Any], 
                    base_url: str, on_content: Callable[[str], None]) -> str:
    """Send a streaming request to the API and process chunks."""
    url = f"{base_url}/chat/completions"
    response = requests.post(url, headers=headers, json=data, stream=True, timeout=60)
    
    if response.status_code != 200:
        raise APIError(f"API returned error {response.status_code}: {response.text}")
    
    # Collect the full response while also calling the callback
    full_response = ""
    
    for line in response.iter_lines():
        if not line:
            continue
        
        # Remove the "data: " prefix
        if line.startswith(b"data: "):
            line = line[6:]
        
        # "[DONE]" marks the end of the stream
        if line == b"[DONE]":
            break
            
        try:
            chunk = json.loads(line)
            if "choices" in chunk and chunk["choices"]:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    content = delta["content"]
                    full_response += content
                    on_content(content)
        except json.JSONDecodeError:
            pass
    
    return full_response 