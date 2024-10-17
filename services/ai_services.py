import os
import requests
import openai, anthropic
from retry import retry
import aiohttp
from config import Config

OPENAI_API_KEY = Config.OPENAI_API_KEY
CLAUDE_API_KEY = Config.CLAUDE_API_KEY

@retry(tries=3, delay=2, backoff=2)
async def call_openai_api(prompt, session=None):
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",  # Verify the correct model name
        "messages": [
            {"role": "system", "content": "You are an assistant that answers questions based on provided JSON data."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    if session is None:
        async with aiohttp.ClientSession() as session:
            return await fetch_openai_result(session, api_url, headers, data)
    else:
        return await fetch_openai_result(session, api_url, headers, data)

async def fetch_openai_result(session, api_url, headers, data):
    try:
        async with session.post(api_url, headers=headers, json=data) as response:
            response_data = await response.json()
            if response.status == 200:
                # Log or print the full response for debugging
                print("Full response:", response_data)
                if 'choices' in response_data:
                    return response_data['choices'][0]['message']['content'].strip()
                else:
                    raise RuntimeError("Unexpected response structure: 'choices' not found")
            else:
                error_detail = await response.text()
                raise RuntimeError(f"OpenAI API request failed with status {response.status}: {error_detail}")
    except aiohttp.ClientError as e:
        raise RuntimeError(f"OpenAI API request failed: {str(e)}")

@retry(tries=3, delay=2, backoff=2)
def call_claude_api(prompt):
    try:
        client = anthropic.Anthropic(
            api_key = CLAUDE_API_KEY
        )
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=100,
            messages=[
                {"role": "user", "content": prompt[:190000]}
            ]
        )
        print(message.content['text'])
        return message.content
    except Exception as e:
        raise RuntimeError(f"Claude API request failed: {str(e)}")