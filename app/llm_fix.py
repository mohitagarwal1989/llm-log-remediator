from typing import List, Tuple
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from app.config import GROQ_API_KEY

# ------------------------------------------------------------------
# LangChain LLM
# ------------------------------------------------------------------
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-120b",
    temperature=0.2,
    max_tokens=1000,
)


# ------------------------------------------------------------------
# Structured Output
# ------------------------------------------------------------------
class FixResponse(BaseModel):
    root_cause: str =  Field(...)
    fix: str =  Field(...)
    
    confidence: float = Field(
        default=0.0,
        description="Confidence score between 0.0 and 1.0"
    )



parser = PydanticOutputParser(pydantic_object=FixResponse)


# ------------------------------------------------------------------
# Prompt Templates
# ------------------------------------------------------------------
FIX_PROMPT = PromptTemplate(
    input_variables=["stack_trace", "repo_files"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template="""
You are a senior Java production engineer.

IMPORTANT CONSTRAINTS:
- Work ONLY on the specific exception shown in the stack trace below.
- Do NOT speculate about unrelated issues.
- Do NOT suggest refactors, optimizations, or improvements unrelated to the error.
- Base your analysis STRICTLY on the stack trace and the provided files.
- If the exact root cause cannot be determined, clearly state the most likely cause directly tied to the exception.

Exception stack trace:
{stack_trace}

Your tasks:
1. Identify the direct root cause of THIS exception only.
2. Propose a minimal, targeted fix that resolves THIS exception.
3. Provide a confidence score between 0.0 and 1.0.

OUTPUT RULES (MANDATORY):
- Return ONLY valid JSON.
- ALL fields in the schema MUST be present.
- Do NOT include explanations, markdown, or extra text.
- If unsure, still return valid JSON with empty strings and confidence 0.0.
- Do NOT stop early or truncate the response.

{format_instructions}
""")

JAVA_REWRITE_PROMPT = PromptTemplate(
    input_variables=["file_path", "original_content", "fix"],
    template="""
You are a Java code editor.

CRITICAL RULES:
- Modify the file ONLY if the fix explicitly applies to THIS file.
- If the fix refers to another class, service, repository, or file, do NOT modify this file.
- If no change is required in this file, output EXACTLY the single token: __NO_CHANGE__
- Do NOT invent changes.
- Do NOT move logic between layers.
File path:
{file_path}

Original file content:
{original_content}

Fix to apply:
{fix}

OUTPUT RULES:
- If editing is required, output ONLY the FULL updated Java file content.
- Do NOT output explanations, diffs, markdown, or extra text.
- If no change is required, output ONLY: __NO_CHANGE__
"""
)


# ------------------------------------------------------------------
# Chains
# ------------------------------------------------------------------
fix_chain = FIX_PROMPT | llm | parser
rewrite_chain = JAVA_REWRITE_PROMPT | llm


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

async def get_fix_from_llm(stack_trace: str, repo_files: List[str]) -> Tuple[str, float]:
    print("🔮 Fetching fix from LLM (LangChain)")

    result: FixResponse = await fix_chain.ainvoke(
        {"stack_trace": stack_trace}
    )

    confidence = min(max(result.confidence, 0.0), 1.0)

    
    if "confidence" not in result.model_fields_set:
        print("⚠ LLM did not return confidence — defaulting to 0.0")


    print("print from get fix from llm", result)

    print("✅ LLM Root Cause:", result.root_cause)
    print("✅ LLM Confidence:", result.confidence)

    return result.fix.strip(), confidence    


async def get_updated_java_file(
    file_path: str,
    original_content: str,
    fix: str
) -> str:
    response = await rewrite_chain.ainvoke(
        {
            "file_path": file_path,
            "original_content": original_content,
            "fix": fix,
        }
    )

    print("print from get updated file", response)

    
    output = response.content.strip()
    if output == "__NO_CHANGE__":
        return original_content

    return output
