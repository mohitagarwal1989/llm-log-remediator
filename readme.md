# LLM Log Remediator

Fully automated system that:
- watches production logs
- detects Java exceptions
- uses an LLM to generate fixes
- safely applies code changes
- creates GitHub pull requests

## Spring Exception Structure in Logs

A **single Spring exception** written to application logs may span multiple lines and must be treated as **one logical error**, not multiple exceptions.

A typical Spring exception may contain the following parts:

1. **Log event line**  
   - Includes timestamp, log level (`ERROR`), thread info, logger name, and summary message  
   - Example: `timestamp + ERROR + message`

2. **Optional blank line**  
   - Separates the log header from the Java exception details

3. **Exception class line**  
   - Example: `java.util.NoSuchElementException: data not exist`

4. **Stack frames**  
   - One or more lines starting with `at ...`

5. **Optional `Caused by:` blocks**  
   - Nested or root cause exceptions, each with their own stack frames

---

## Rules for Reading Errors / Exceptions from Log Files

When parsing log files programmatically, **continue reading lines as part of the same exception as long as ANY of the following conditions are true**:

- ✅ The line **starts with whitespace**  
  → Indicates a stack frame or continued stack trace line

- ✅ The line **starts with `at `**  
  → Java stack frame

- ✅ The line **starts with `Caused by:`**  
  → Nested or root cause of the same exception

- ✅ The line **contains an exception class name**  
  → e.g. `Exception`, `RuntimeException`, `Error`

- ✅ The line is **blank but occurs inside an active stack trace**  
  → Blank lines are valid within a single exception block

- ✅ The line **does NOT start with a new timestamp**  
  → Indicates continuation of the current log event

---

## When to Stop Reading

Stop collecting lines for the current exception when:

- ❌ A line **starts with a new timestamp** (indicating a new log entry), or  
- ❌ A line does **not match any of the continuation rules above**

---

## Key Takeaway

> **A Spring exception is a multi‑line construct.**  
> Always group log lines together until a new timestamped log entry is encountered, to avoid split or duplicate exceptions.

## Run
```bash
pip install pyproject.toml
python run.py
python run_api.py

