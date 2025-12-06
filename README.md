# JobApplier.AI

AI-powered job-application automation combining Playwright browser automation with LLM helpers to parse job postings and
auto-fill “Easy Apply” flows (currently implemented for LinkedIn).

---

## Quickstart (macOS)

1. Clone / open the workspace in VS Code (project root = repository root).
2. Create and activate a Python venv:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies and Playwright browsers:

```bash
pip install -r requirements.txt
playwright install
```

4. Provide API keys:

- OpenAI: set env var or place key in keys/openai-key.txt

```bash
export OPENAI_API_KEY="sk-..."
```

- (Optional) Gemini: export GEMINI_API_KEY or place in keys/gemini-key.txt

5. Add user data:

- Put a single resume file in `my_data/resume/`
- Edit `my_data/qna_list.txt` with extra user facts (optional)

6. Run:

```bash
python src/main.py
```

---

## Project structure (important files)

- src/main.py — entrypoint: boots Playwright and starts the LinkedIn Easy Apply flow.
- src/config.py — configuration constants, paths, and API-key resolution helpers.
- src/linkedin/
    - easy_apply.py — top-level orchestration for scanning and applying.
    - job_search.py — fetch job list, click job cards.
    - application_flow.py — per-job apply logic.
    - dom_parser.py — extract form fields and step controls from Easy Apply modal.
    - form_filler.py — fill text/select/combobox fields.
    - constants.py — timing and selector constants.
- src/ai/
    - openai_provider.py — OpenAI/Responses API integration, resume upload, parse_form tool.
    - gemini_provider.py — optional Gemini provider.
    - ai_helper.py — shared helpers.
- src/utils/
    - qna_manager.py — AI + cache interface for answering form questions.
    - cache_manager.py — prompt/QnA cache persisted to sys_data/.
    - run_data_manager.py — run metadata and application history.
    - user_data_manager.py — resume discovery and qna_list handling.
    - json_utils.py, csv_utils.py, txt_utils.py — helpers.
- Data folders (configured in src/config.py):
    - my_data/ — user assets (resume, qna_list.txt)
    - sys_data/ — caches and runtime state (qnas_cache.json, run_data.json)
    - keys/ — local API keys (git-ignored)

---

## Configuration & keys

- Primary config in `src/config.py`. Important variables:
    - OPENAI_MODEL, OPENAI_API_KEY resolution, LINKEDIN_STATE_FILE, HIDE_BROWSER.
- Key lookup order for OpenAI:
    1. Environment variable `OPENAI_API_KEY`
    2. `keys/openai-key.txt` (fallback)
- Keep `keys/`, `my_data/`, and `sys_data/` out of version control (they are git-ignored).

---

## Runtime flow (high level)

1. main.py launches Playwright Chromium and restores/creates LinkedIn session.
2. easy_apply scans job cards (job_search.fetch_job_list).
3. For each job:
    - application_flow.apply_job evaluates relevancy (AI), opens job modal.
    - dom_parser.extract_form_fields extracts controls.
    - form_filler.fill_all_fields fills inputs using qna_manager to get answers (caching + AI).
4. run_data_manager and cache_manager persist application metadata and QnA cache.

---

## Development & debugging

- VS Code launch config: `.vscode/launch.json` (runs `src/main.py` with PYTHONPATH).
- To force a fresh LinkedIn login, delete the file at path `LINKEDIN_STATE_FILE` (configured in `src/config.py`).
- Reset caches by deleting `sys_data/qnas_cache.json` and/or `sys_data/run_data.json`.
- If selectors break after a LinkedIn UI update, edit selectors in:
    - `src/linkedin/dom_parser.py`
    - `src/linkedin/application_flow.py`
    - `src/linkedin/job_search.py`

Notes:

- Headed vs headless: set `HIDE_BROWSER` in `src/config.py` — some elements are different in headless mode.
- get_resume_file expects a single resume file under `my_data/resume/`.

---

## Common pitfalls

- Multiple files in `my_data/resume/` — keep only one resume file.
- Missing or invalid OpenAI key — AI calls will fail.
- Playwright browsers not installed — run `playwright install`.
- LinkedIn UI changes require selector updates.

---

## Extensibility

- Add other platforms by creating a package under `src/` similar to `src/linkedin/`.
- Add AI providers by implementing the same provider interface patterns in `src/ai/` and wiring into
  `src/utils/qna_manager.py`.
- Improve parsing by adjusting `dom_parser` or the `parse_form` tool in `openai_provider.py`.

---

## Where to look first (recommended order)

1. `src/main.py`
2. `src/linkedin/easy_apply.py`
3. `src/linkedin/application_flow.py` and `src/linkedin/form_filler.py`
4. `src/ai/openai_provider.py` and `src/utils/qna_manager.py`
5. `src/config.py` (paths & keys)

---

## Troubleshooting quick fixes

- Playwright errors: run `playwright install` and ensure Chromium is available.
- Permission/file errors: ensure `my_data/` and `sys_data/` exist and are writable.
- Slow or rate-limited AI responses: check API quotas and model configuration (`OPENAI_MODEL` in config).

---

If you want, I can:

- Commit this README.md into the workspace for you.
- Add a short CONTRIBUTING.md or Troubleshooting section with concrete errors and fixes.

```// filepath: /Users/premranjan/code/learn/JobApplier.AI/README.md

# JobApplier.AI

AI-powered job-application automation combining Playwright browser automation with LLM helpers to parse job postings and auto-fill “Easy Apply” flows (currently implemented for LinkedIn).

---

## Quickstart (macOS)

1. Clone / open the workspace in VS Code (project root = repository root).
2. Create and activate a Python venv:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies and Playwright browsers:

```bash
pip install -r requirements.txt
playwright install
```

4. Provide API keys:

- OpenAI: set env var or place key in keys/openai-key.txt

```bash
export OPENAI_API_KEY="sk-..."
```

- (Optional) Gemini: export GEMINI_API_KEY or place in keys/gemini-key.txt

5. Add user data:

- Put a single resume file in `my_data/resume/`
- Edit `my_data/qna_list.txt` with extra user facts (optional)

6. Run:

```bash
python src/main.py
```

---