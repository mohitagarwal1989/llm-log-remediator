import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO_URL = os.environ.get("GITHUB_REPO_URL")
GITHUB_LOCAL_PATH = os.environ.get("GITHUB_LOCAL_PATH")
GITHUB_BASE_BRANCH = os.environ.get("GITHUB_BASE_BRANCH", "master")

LOG_FOLDERS = os.environ.get("LOG_FOLDERS", "").split(",")
SCAN_INTERVAL = int(os.environ.get("SCAN_INTERVAL", 60))
LLM_CONFIDENCE_THRESHOLD = 0.8

OFFSET_FILE = "log_offsets.json"

if not all([GROQ_API_KEY, GITHUB_TOKEN, GITHUB_REPO_URL]):
    raise RuntimeError("Missing required environment variables")