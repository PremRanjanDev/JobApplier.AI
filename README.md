# JobApplier.AI

AI-powered Job Application Automation

## Features
- Automates LinkedIn job search and Easy Apply using Playwright and AI
- Uses OpenAI (or other providers) to parse job listings and fill application forms
- Modular AI provider support (OpenAI, Gemini, etc.)
- Clean, scalable Python package structure

## Project Structure
```
scripts/
  apply_from_linkedin.py   # Script to Start the LinkedIn Easy Apply process
src/
  ai/
    ai_utils.py            # Provider-agnostic AI abstraction layer
    ai_provider_openai.py  # OpenAI-specific logic
    __init__.py
  linkedin/
    easy_apply.py          # Main job application logic
    login.py               # LinkedIn login automation
    __init__.py
  utils/
    json_utils.py          # JSON file utilities
    csv_utils.py           # CSV file utilities
    __init__.py
output/
  linkedin/                # Application logs and results
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
### From the Terminal
- **From the project root:**
  ```sh
  PYTHONPATH=src python3 -m linkedin
  ```
  or to run the script directly (with correct imports):
  ```sh
  PYTHONPATH=. python3 scripts/apply_from_linkedin.py
  ```

### Debugging in VS Code
1. Open the project in VS Code.
2. Go to the Run and Debug panel (play icon with a bug).
3. Select **"Debug LinkedIn Script"** (or your custom config) from the dropdown.
4. Press F5 or click the green Start Debugging button.

**Sample `.vscode/launch.json`:**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug LinkedIn Script",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/scripts/apply_from_linkedin.py",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

- This ensures all imports work and you can set breakpoints anywhere in your code.

## Notes
- Always use absolute imports in your code (e.g., `from ai.ai_utils import ...`).
- Do not run files directly from inside subfolders; always use the correct `PYTHONPATH`.
- The project is designed for easy extension to other AI providers and job platforms.

## Clear user login data
To clear saved LinkedIn login state, delete the file:
```
user_data/linkedin_state.json
```

---

**Happy job hunting with AI!**
