import re
import aiofiles
from typing import Set

STACK_TRACE_START = re.compile(r'([\w\.]+Exception|[\w]+Error)')
STACK_TRACE_LINE  = re.compile(r'^\s+at\s+|^Caused by:')
JAVA_FILE_REGEX   = re.compile(r'\(([\w$]+\.java):(\d+)')
EXCEPTION_REGEX = re.compile(r'([\w\.]+Exception|[\w]+Error)')
TIMESTAMP_LINE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}"
)

STACK_CONTINUATION = re.compile(
    r"^\s+at |^at |^Caused by:|Exception|Error"
)


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
    started = False

    async with aiofiles.open(file_path, "r", errors="ignore") as f:
        await f.seek(start_offset)

        async for line in f:
            stripped = line.rstrip()

            # Start when we hit the original ERROR log
            if not started:
                if "ERROR" in stripped and "exception" in stripped.lower():
                    started = True
                    lines.append(stripped)
                else:
                    break
                continue

            # Stop only when we hit a NEW log entry (timestamp)
            if TIMESTAMP_LINE.match(stripped):
                break

            # Accept valid stack trace content
            if (
                stripped == ""
                or STACK_CONTINUATION.search(stripped)
            ):
                lines.append(stripped)
            else:
                break

        end_offset = await f.tell()

    return "\n".join(lines), end_offset
