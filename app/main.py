import asyncio
import os
from app.config import LOG_FOLDERS, SCAN_INTERVAL
from app.model import load_model
from app.scanner import load_offsets, scan_folder
from app.repo_ops import load_github_repo

async def start():
    REQUIRED_ENV_VARS = [
        "GROQ_API_KEY",
        "GITHUB_TOKEN",
        "GITHUB_REPO_URL",
        "GITHUB_LOCAL_PATH",
    ]

    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    load_offsets()
    await load_model()
    load_github_repo()

    print("🚀 Log monitoring started")

    while True:
        tasks = [
            scan_folder(folder)
            for folder in LOG_FOLDERS
            if os.path.isdir(folder)
        ]
        await asyncio.gather(*tasks)
        print(f"⏳ Sleeping {SCAN_INTERVAL} seconds\n")
        await asyncio.sleep(SCAN_INTERVAL)