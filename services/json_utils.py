import json
from config import Config
import hashlib
import aiohttp
import asyncio
from services.ai_services import call_openai_api
from services.cache import cache_summary, get_cached_summary

def calculate_file_hash(json_data):
    """Calculate a hash of the JSON data for reliable caching."""
    return hashlib.md5(json.dumps(json_data, sort_keys=True).encode()).hexdigest()

def chunk_json(json_data, chunk_size=1000):
    """Chunk JSON data into smaller pieces for summarization."""
    json_str = json.dumps(json_data)
    json_length = len(json_str)
    chunks = [json_str[i:i + chunk_size] for i in range(0, json_length, chunk_size)]
    return chunks

async def summarize_chunks(chunks):
    """Summarize chunks asynchronously."""
    async with aiohttp.ClientSession() as session:
        tasks = [call_openai_api(chunk, session) for chunk in chunks]
        return await asyncio.gather(*tasks)

def summarize_json(json_data, filename):
    """Summarize JSON data by chunking and calling the API, with caching."""

    file_hash = calculate_file_hash(json_data)

    # Check if the summary is already cached
    cached_summary = get_cached_summary(file_hash)
    if cached_summary:
        return cached_summary

    # If not cached, proceed to chunk and summarize
    chunks = chunk_json(json_data)
    summaries = asyncio.run(summarize_chunks(chunks))
    
    combined_summary = " ".join(summaries)
    cache_summary(file_hash, combined_summary)

    return combined_summary

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_prompt(json_data, query, history=None):
    """Generate a prompt for the AI model using the JSON data and user query."""
    history_prompt = "\n".join([f"User: {h['query']}\nAssistant: {h['answer']}" for h in history]) if history else ""
    prompt = f"""You are an assistant that answers questions based solely on the following JSON data. You need to answer to the point, do not give the steps that you followed to get the answer. Just return the answer to the question. If the question cannot be answered using the data, respond with: "{Config.FALLBACK_MESSAGE}"

    
Previous interactions:
{history_prompt}

JSON Data:
{json.dumps(json_data, indent=2)}

Question:
{query}

Answer:"""
    return prompt

def is_query_answerable(response):
    """Check if the AI's response is the fallback message."""
    return response != Config.FALLBACK_MESSAGE
