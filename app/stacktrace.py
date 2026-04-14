import re
import aiofiles
from typing import Set

STACK_TRACE_START = re.compile(r'([\w\.]+Exception|[\w]+Error)')
STACK_TRACE_LINE  = re.compile(r'^\s+at\s+|^Caused by:')
JAVA_FILE_REGEX   = re.compile(r'\(([\w$]+\.java):(\d+)')
EXCEPTION_REGEX = re.compile(r'([\w\.]+Exception|[\w]+Error)')

def extract_exception_name(line):
    m = EXCEPTION_REGEX.search(line) or line.strip()
    return m.group(1) if m else None

def is_stack_start(line: str) -> bool:
    return bool(STACK_TRACE_START.search(line))

def extract_java_files_from_stacktrace(stack_trace: str) -> Set[str]:
    print("extracting file names from stacktrace")
    return {name for name, _ in JAVA_FILE_REGEX.findall(stack_trace)}

async def extract_full_stack_trace(file_path: str, start_offset: int):
    lines = []

    async with aiofiles.open(file_path, "r", errors="ignore") as f:
        await f.seek(start_offset)

        async for line in f:
            if not lines:
                if STACK_TRACE_START.search(line):
                    lines.append(line.rstrip())
                else:
                    break
            else:
                if STACK_TRACE_LINE.search(line):
                    lines.append(line.rstrip())
                else:
                    break

        end_offset = await f.tell()

    return "\n".join(lines), end_offset    