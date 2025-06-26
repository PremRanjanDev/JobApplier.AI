import datetime
from google import genai

def ask_gemini(prompt: str, model: str = "gemini-2.5-flash"):
    """
    Sends a prompt to Google's Gemini API and returns the raw output text.
    """
    print("Sending prompt to Google Gemini...")
    with open('keys/gemini-key.txt', 'r') as f:
        gemini_api_key = f.read().strip()
    if not gemini_api_key:
        raise RuntimeError("Gemini API key not found in keys/gemini-key.txt")
    client = genai.Client(api_key=gemini_api_key)

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text

if __name__ == "__main__":
    now = datetime.datetime.now()
    print(now.isoformat())
    response = ask_gemini("Write a one-sentence bedtime story about a unicorn.")
    print("Time taken: ", datetime.datetime.now() - now)
    print(response)
