import aiofiles
import json
import os
from app.stacktrace import is_stack_start, extract_full_stack_trace
from app.config import OFFSET_FILE
from typing import Dict
from app.remediation import handle_error

file_offsets: Dict[str, int] = {}

def load_offsets():
    global file_offsets
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            file_offsets = json.load(f)

def save_offsets():
    with open(OFFSET_FILE, "w") as f:
        json.dump(file_offsets, f)

async def scan_file(file_path: str):
    current_size = os.path.getsize(file_path)
    last_offset = file_offsets.get(file_path, 0)

    
# ✅ Reset offset if file was truncated or replaced
    if last_offset > current_size:
        last_offset = 0
        file_offsets[file_path] = 0
        save_offsets()


    async with aiofiles.open(file_path, "r", errors="ignore") as f:
        await f.seek(last_offset)

        while True:
            pos = await f.tell()
            line = await f.readline()
            if not line:
                break

            if is_stack_start(line):
                trace, new_offset = await extract_full_stack_trace(
                    file_path, pos
                )
                await handle_error(file_path, trace)
                file_offsets[file_path] = new_offset
                save_offsets()
                await f.seek(new_offset)

        file_offsets[file_path] = await f.tell()
        save_offsets()

async def scan_folder(folder: str):
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            await scan_file(os.path.join(folder, file))        