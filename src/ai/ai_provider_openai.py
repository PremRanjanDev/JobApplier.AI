import asyncio
from openai import OpenAI

async def get_openai_response(prompt: str, model: str = "gpt-4.1"):
    """
    Sends a prompt to OpenAI's Responses API and returns the raw output text.
    """
    with open('keys/openai-key.txt', 'r') as f:
        openai_api_key = f.read().strip()
    if not openai_api_key:
        raise RuntimeError("OpenAI API key not found in keys/openai-key.txt")
    client = OpenAI(api_key=openai_api_key)

    loop = asyncio.get_event_loop()
    def sync_call():
        response = client.responses.create(
            model=model,
            input=prompt
        )
        return response.output_text
    text = await loop.run_in_executor(None, sync_call)
    return text

async def basic_openai_test():
    """A basic test function that sends a prompt to OpenAI and prints the response."""
    text = await get_openai_response("Write a one-sentence bedtime story about a unicorn.")
    print(text)

if __name__ == "__main__":
    asyncio.run(basic_openai_test())
