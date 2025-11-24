"""Configuration management for JobApplier.AI"""
import os
from pathlib import Path

# Job search parameters
JOB_KEYWORDS = "Java react"
JOB_LOCATION = "Singapore"

# Apply only relevant jobs on or above
RELEVANCY_PERCENTAGE = 80

# Exclude companies
EXCLUDE_COMPANIES = []

# Browser settings
HIDE_BROWSER = False  # Run headless
OPEN_MAXIMIZED = True

# OpenAI model
OPENAI_MODEL = "gpt-5-mini"

# Job application settings
CONNECT_RECRUITER = True
MESSAGE_RECRUITER = True

# Base directories
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
MY_DATA_DIR = BASE_DIR / "my_data"
SYS_DATA_DIR = BASE_DIR / "sys_data"
KEYS_DIR = BASE_DIR / "keys"
OUTPUT_DIR = BASE_DIR / "output"

# User data paths
OTHER_INFO_FILE = MY_DATA_DIR / "other_info.txt"
RESUME_FOLDER = MY_DATA_DIR / "resume"

# System data paths
CACHE_FILE = SYS_DATA_DIR / "qnas_cache.json"
RUN_DATA_FILE = SYS_DATA_DIR / "run_data.json"
OTHER_INFO_TRAINED_FILE = SYS_DATA_DIR / "other_info_trained.txt"
LINKEDIN_STATE_FILE = SYS_DATA_DIR / "login" / "linkedin_state.json"

# API Keys (prefer environment variables)
OPENAI_KEY_FILE = KEYS_DIR / "openai-key.txt"
GEMINI_KEY_FILE = KEYS_DIR / "gemini-key.txt"

def get_openai_key():
    """Get OpenAI API key from environment or file"""
    key = os.getenv("OPENAI_API_KEY")
    if not key and OPENAI_KEY_FILE.exists():
        key = OPENAI_KEY_FILE.read_text().strip()
    return key

def get_gemini_key():
    """Get Gemini API key from environment or file"""
    key = os.getenv("GEMINI_API_KEY")
    if not key and GEMINI_KEY_FILE.exists():
        key = GEMINI_KEY_FILE.read_text().strip()
    return key

# Ensure directories exist
for directory in [MY_DATA_DIR, SYS_DATA_DIR, KEYS_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
