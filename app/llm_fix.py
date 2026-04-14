from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

# -------------------------------------------------
# LLM – FIX REASONING ONLY
# -------------------------------------------------
async def get_fix_from_llm(stack_trace: str) -> str:
    print("fix not found in error collection, so getting fix from llm")
    prompt = f"""
You are a senior Java production engineer.

Exception stack trace:
{stack_trace}

Explain the root cause and propose a fix.
Respond ONLY with the Fix (concise, no code block).
"""
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()

# -------------------------------------------------
# LLM – FULL FILE REWRITE (OPTION A)
# -------------------------------------------------
async def get_updated_java_file(
    file_path: str,
    original_content: str,
    fix: str
) -> str:

    print("calling llm to get updated files")
    system_prompt = (
        "You are a Java code editor.\n"
        "You modify existing files.\n"
        "Output ONLY the full updated file content.\n"
        "Do NOT output explanations, diffs, or markdown."
    )

    user_prompt = f"""
File path:
{file_path}

Original file content:
{original_content}

Fix to apply:
{fix}

Return the FULL updated file content only.
"""

    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.05,
        max_tokens=2000,
        stop=["```"],
    )

    return resp.choices[0].message.content.strip()      
