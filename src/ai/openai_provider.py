from openai import OpenAI

def get_openai_response(prompt: str, model: str = "gpt-4.1"):
    """
    Sends a prompt to OpenAI's Responses API and returns the raw output text.
    """
    with open('keys/openai-key.txt', 'r') as f:
        openai_api_key = f.read().strip()
    if not openai_api_key:
        raise RuntimeError("OpenAI API key not found in keys/openai-key.txt")
    client = OpenAI(api_key=openai_api_key)

    response = client.responses.create(
        model=model,
        input=prompt
    )
    # Extract the output text from the response object
    return response.output_text

def basic_openai_test():
    """A basic test function that sends a prompt to OpenAI and prints the response."""
    response = get_openai_response("Write a one-sentence bedtime story about a unicorn.")
    print(response.output_text)

if __name__ == "__main__":
    basic_openai_test()
