import os
from app.stacktrace import extract_exception_name, extract_java_files_from_stacktrace
from app.storage import find_fix_for_error, store_fix_in_kb, store_exception_log, extract_fix_only
from app.llm_fix import get_fix_from_llm, get_updated_java_file
from app.repo_ops import apply_changes_and_raise_pr, find_java_files_in_repo, prepare_repo_clean_state
from app.config import GITHUB_LOCAL_PATH

async def handle_error(file_path: str, stack_trace: str):
    print("⚠ Exception detected:\n", stack_trace)
    print("file path: ", file_path)

    exception = extract_exception_name(stack_trace)
    print("exception name: ", exception)
    if not exception:
        print("exception is none or empty")
        return
    fix = await find_fix_for_error(exception)
    print("fix----", fix)
    if not fix:
        llm_fix = await get_fix_from_llm(stack_trace)
        await store_fix_in_kb(exception, llm_fix)
        fix = extract_fix_only(llm_fix)

    java_files = extract_java_files_from_stacktrace(stack_trace)
    print("files from stacktrace", java_files)
    if not java_files:
        print("❌ No Java files found in stack trace")
        return

    repo_files = find_java_files_in_repo(GITHUB_LOCAL_PATH, java_files)
    print("files from repo", repo_files)
    if not repo_files:
        print("❌ Java files not found in repo")
        return

    changes_made = False       
    prepare_repo_clean_state()
    for rel_path, content in repo_files.items():
        updated = await get_updated_java_file(rel_path, content, fix)

        if updated != content:
            full_path = os.path.join(GITHUB_LOCAL_PATH, rel_path)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(updated)
            changes_made = True

    exception_name = stack_trace.splitlines()[0]
    if changes_made:
        apply_changes_and_raise_pr(exception_name)
        await store_exception_log(file_path, exception)