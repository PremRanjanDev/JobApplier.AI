from openai import OpenAI

def ask_openai(prompt: str, model: str = "gpt-4.1"):
    """
    Sends a prompt to OpenAI's Responses API and returns the raw output text.
    """
    print("Sending prompt to OpenAI...")
    with open('keys/openai-key.txt', 'r') as f:
        openai_api_key = f.read().strip()
    if not openai_api_key:
        raise RuntimeError("OpenAI API key not found in keys/openai-key.txt")
    client = OpenAI(api_key=openai_api_key)

    response = client.responses.create(
        model=model,
        input=prompt
    )
    return response.output_text


if __name__ == "__main__":
    response = ask_openai("Write a one-sentence bedtime story about a unicorn.")
    print(response)
