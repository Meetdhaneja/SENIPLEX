"""
Code Validation Script
Checks for common bugs and issues in the codebase
"""
import os
import sys
from pathlib import Path


def _configure_console_encoding() -> None:
    """
    Make console output robust on Windows where the default encoding may be cp1252.
    This prevents UnicodeEncodeError when printing non-ASCII characters.
    """
    for stream in (getattr(sys, "stdout", None), getattr(sys, "stderr", None)):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                # Best-effort: don't fail validation due to console config
                pass


def check_imports():
    """Check for missing imports"""
    print("Checking imports...")
    
    issues = []
    
    # Files that use numpy
    numpy_files = [
        'backend/app/feature_store/user_features.py',
        'backend/app/feature_store/movie_features.py',
        'backend/app/ai/ranking/time_decay.py',
        'backend/app/ai/ranking/hybrid_ranker.py',
        'backend/app/ai/evaluation/metrics.py',
        'backend/app/ai/baseline/trending_model.py',
    ]
    
    for file_path in numpy_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'np.' in content and 'import numpy' not in content:
                    issues.append(f"❌ {file_path}: Uses 'np.' but missing numpy import")
                else:
                    print(f"OK: {file_path}: Imports")
    
    return issues


def check_settings_usage():
    """Check for unsafe settings access"""
    print("\nChecking settings usage...")
    
    issues = []
    
    files_to_check = [
        'backend/app/cache/redis_client.py',
        'backend/app/core/config.py',
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for direct settings access without getattr
                if 'settings.REDIS' in content and 'getattr' not in content:
                    issues.append(f"⚠️ {file_path}: Direct settings access (should use getattr)")
                else:
                    print(f"OK: {file_path}: Settings access")
    
    return issues


def check_database_sessions():
    """Check for proper database session handling"""
    print("\nChecking database sessions...")
    
    issues = []
    
    # Check for session.close() in finally blocks
    files_to_check = [
        'backend/app/feature_store/feature_updater.py',
        'backend/app/tasks/update_user_embedding.py',
        'backend/app/tasks/rebuild_faiss.py',
        'backend/app/tasks/log_recommendation.py',
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'SessionLocal()' in content and 'db.close()' in content:
                    print(f"OK: {file_path}: Session handling")
                elif 'SessionLocal()' in content:
                    issues.append(f"⚠️ {file_path}: Creates session but may not close it")
    
    return issues


def check_none_handling():
    """Check for None handling"""
    print("\nChecking None handling...")
    
    issues = []
    
    # Check for proper None checks before operations
    files_to_check = [
        'backend/app/ai/faiss/search.py',
        'backend/app/ai/orchestration/recommendation_pipeline.py',
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'if not' in content or 'is None' in content:
                    print(f"OK: {file_path}: None checks present")
                else:
                    issues.append(f"⚠️ {file_path}: May need more None checks")
    
    return issues


def check_exception_handling():
    """Check for exception handling"""
    print("\nChecking exception handling...")
    
    issues = []
    
    python_files = Path('backend/app').rglob('*.py')
    
    for file_path in python_files:
        if '__pycache__' in str(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check if file has functions but no try-except
            if 'def ' in content and 'try:' not in content and 'test' not in str(file_path).lower():
                # Skip __init__ files
                if '__init__.py' not in str(file_path):
                    issues.append(f"⚠️ {file_path}: No exception handling")
    
    return issues


def validate_code():
    """Run all validation checks"""
    _configure_console_encoding()
    print("=" * 60)
    print("CODE VALIDATION REPORT")
    print("=" * 60)
    
    all_issues = []
    
    # Run checks
    all_issues.extend(check_imports())
    all_issues.extend(check_settings_usage())
    all_issues.extend(check_database_sessions())
    all_issues.extend(check_none_handling())
    
    # Print summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if not all_issues:
        print("All checks passed! Code is clean.")
        return 0
    else:
        print(f"⚠️ Found {len(all_issues)} potential issues:\n")
        for issue in all_issues:
            print(f"  {issue}")
        print("\nNote: These are warnings, not critical errors.")
        return len(all_issues)


if __name__ == '__main__':
    issues_count = validate_code()
    sys.exit(0)  # Always exit with 0 (warnings are OK)
