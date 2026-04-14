# LLM Log Remediator

Fully automated system that:
- watches production logs
- detects Java exceptions
- uses an LLM to generate fixes
- safely applies code changes
- creates GitHub pull requests

## Run
```bash
pip install pyproject.toml
python run.py
python run_api.py