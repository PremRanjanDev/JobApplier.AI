# JobApplier.AI

AI-powered Job Application Automation

## Features
- Automates LinkedIn job search and Easy Apply using Playwright and AI
- Uses OpenAI (or other providers) to parse job listings and fill application forms
- Modular AI provider support (OpenAI, Gemini, etc.)
- Clean, scalable Python package structure

## Project Structure
```
src/
  main.py                  # Main entry point for running the job application automation
  ai/
    ai_utils.py            # Provider-agnostic AI abstraction layer
    openai_provider.py     # OpenAI-specific logic
    __init__.py
  linkedin/
    easy_apply.py          # LinkedIn job application logic
    login.py               # LinkedIn login automation
    __init__.py
  utils/
    json_utils.py          # JSON file utilities
    csv_utils.py           # CSV file utilities
    __init__.py
output/                    # Application logs and results
  linkedin/
keys/
  openai-key.txt           # Your OpenAI API key
user_data/
  linkedin_state.json      # Saved LinkedIn session state
```

## Setup
1. **Install dependencies:**
   ```sh
   pip install playwright openai
   playwright install
   ```
2. **Add your OpenAI API key:**
   - Place your key in `keys/openai-key.txt` (one line, no spaces).
3. **(Optional) Clean login state:**
   - To clear saved LinkedIn login, delete `user_data/linkedin_state.json`.

## How to Run

### From the command line

```sh
python src/main.py
```

You will be prompted for your LinkedIn credentials, job keyword, and location.

### Debug in VS Code

- Use the provided `.vscode/launch.json` configuration.
- The entry point is now `src/main.py`.
- Make sure your `PYTHONPATH` includes the project root for absolute imports.

## Notes
- Always use absolute imports in your code (e.g., `from ai.ai_utils import ...`).
- Do not run files directly from inside subfolders; always use the correct `PYTHONPATH`.
- The project is designed for easy extension to other AI providers and job platforms.

## Clear user login data
To clear saved login state, delete the files (as required):
```
user_data/linkedin_state.json
```

---

**Happy job hunting with AI!**
