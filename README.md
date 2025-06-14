# JobApplier.AI

Job Applier with AI

## Features
- Automates LinkedIn job search and Easy Apply using Playwright and AI
- Uses OpenAI (or other providers) to parse job listings and fill application forms
- Modular AI provider support (OpenAI, Gemini, etc.)
- Clean, scalable Python package structure

## Project Structure
```
src/
  ai/
    ai_utils.py            # Provider-agnostic AI abstraction layer
    ai_provider_openai.py  # OpenAI-specific logic
    __init__.py
  linkedin/
    easy_apply.py          # Main job application logic
    login.py               # LinkedIn login automation
    __main__.py            # Entry point
    __init__.py
keys/
  openai-key.txt           # Your OpenAI API key
user_data/
  linkedin_state.json      # Saved LinkedIn session state
```

## Setup
1. **Install dependencies:**
   ```zsh
   pip install playwright openai
   playwright install
   ```
2. **Add your OpenAI API key:**
   - Place your key in `keys/openai-key.txt` (one line, no spaces).
3. **(Optional) Clean login state:**
   - To clear saved LinkedIn login, delete `user_data/linkedin_state.json`.

## Notes
- Always use absolute imports in your code (e.g., `from ai.ai_utils import ...`).
- Do not run files directly; always use `-m` with the package/module name.
- The project is designed for easy extension to other AI providers and job platforms.

## Clear user login data
To clear saved LinkedIn login state, delete the file:
```
user_data/linkedin_state.json
```

---

**Happy job hunting with AI!**
