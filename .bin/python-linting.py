#!/usr/bin/env python3
"""
Python linting script for packages_py directory.

Runs ruff linter and py_compile syntax checks on Python files,
with options for auto-fixing and detailed reporting.

Usage:
    # Check all Python files (default)
    python3 .bin/python-linting.py

    # Check with auto-fix
    python3 .bin/python-linting.py --fix

    # Check specific directory
    python3 .bin/python-linting.py --path packages_py/fetch_base_client

    # Syntax check only (py_compile)
    python3 .bin/python-linting.py --syntax-only

    # Output to JSONL file
    python3 .bin/python-linting.py --output logs/python-lint.jsonl

    # Verbose output
    python3 .bin/python-linting.py -v

Error codes ignored by default (configurable):
    - E501: Line too long
    - F401: Unused import
    - F811: Redefinition of unused name
    - F403: Star imports
    - E402: Module level import not at top of file

Based on linting fixes from commit 4cfe6622158be72b30b0cd713ed04b1e26552885
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "target_dir": "packages_py",
    "exclude_patterns": [".venv", "__pycache__", ".git", "node_modules"],
    "ignored_rules": ["E501", "F401", "F811", "F403", "E402"],
    "output_file": None,
}


def find_python_files(target_dir: str, exclude_patterns: List[str]) -> List[str]:
    """Find all Python files in target directory, excluding specified patterns."""
    python_files = []
    target_path = Path(target_dir)

    if not target_path.exists():
        print(f"Error: Directory '{target_dir}' does not exist", file=sys.stderr)
        return []

    for py_file in target_path.rglob("*.py"):
        # Check if any exclude pattern is in the path
        path_str = str(py_file)
        if any(pattern in path_str for pattern in exclude_patterns):
            continue
        python_files.append(str(py_file))

    return sorted(python_files)


def run_syntax_check(python_files: List[str], verbose: bool = False) -> Dict[str, Any]:
    """Run py_compile syntax check on all Python files."""
    results = {
        "total": len(python_files),
        "passed": 0,
        "failed": 0,
        "errors": []
    }

    for py_file in python_files:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", py_file],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                results["passed"] += 1
                if verbose:
                    print(f"  [PASS] {py_file}")
            else:
                results["failed"] += 1
                error_msg = result.stderr.strip() or result.stdout.strip()
                results["errors"].append({
                    "file": py_file,
                    "error": error_msg,
                    "type": "syntax"
                })
                print(f"  [FAIL] {py_file}: {error_msg}")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "file": py_file,
                "error": str(e),
                "type": "exception"
            })

    return results


def run_ruff_check(
    target_dir: str,
    ignored_rules: List[str],
    fix: bool = False,
    verbose: bool = False
) -> Dict[str, Any]:
    """Run ruff linter on target directory."""
    results = {
        "total_errors": 0,
        "fixed": 0,
        "remaining": 0,
        "errors": [],
        "summary": {}
    }

    # Check if ruff is available
    ruff_path = subprocess.run(
        ["which", "ruff"],
        capture_output=True,
        text=True
    )

    if ruff_path.returncode != 0:
        print("Error: ruff is not installed. Install with: pip install ruff", file=sys.stderr)
        return results

    # Build ruff command
    cmd = ["ruff", "check", target_dir]

    if ignored_rules:
        cmd.extend(["--ignore", ",".join(ignored_rules)])

    if fix:
        cmd.append("--fix")

    # Add JSON output for parsing
    cmd.extend(["--output-format", "json"])

    if verbose:
        print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse JSON output
        if result.stdout.strip():
            try:
                errors = json.loads(result.stdout)
                results["errors"] = errors
                results["total_errors"] = len(errors)

                # Categorize by error code
                for error in errors:
                    code = error.get("code", "unknown")
                    if code not in results["summary"]:
                        results["summary"][code] = 0
                    results["summary"][code] += 1

            except json.JSONDecodeError:
                # Fallback to text parsing
                results["raw_output"] = result.stdout

        # Check for "All checks passed"
        if result.returncode == 0:
            results["remaining"] = 0
        else:
            results["remaining"] = results["total_errors"]

    except Exception as e:
        print(f"Error running ruff: {e}", file=sys.stderr)

    return results


def format_ruff_error(error: Dict[str, Any]) -> str:
    """Format a ruff error for display."""
    filename = error.get("filename", "unknown")
    location = error.get("location", {})
    row = location.get("row", "?")
    col = location.get("column", "?")
    code = error.get("code", "???")
    message = error.get("message", "No message")

    return f"{filename}:{row}:{col} [{code}] {message}"


def write_jsonl_output(results: Dict[str, Any], output_file: str) -> None:
    """Write results to JSONL file."""
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

    timestamp = datetime.now().isoformat()

    with open(output_file, "w") as f:
        # Write metadata
        metadata = {
            "type": "metadata",
            "timestamp": timestamp,
            "tool": "python-linting",
            "version": "1.0.0"
        }
        f.write(json.dumps(metadata) + "\n")

        # Write syntax check results
        if "syntax" in results:
            for error in results["syntax"].get("errors", []):
                entry = {
                    "type": "syntax_error",
                    "timestamp": timestamp,
                    **error
                }
                f.write(json.dumps(entry) + "\n")

        # Write ruff results
        if "ruff" in results:
            for error in results["ruff"].get("errors", []):
                entry = {
                    "type": "lint_error",
                    "timestamp": timestamp,
                    "file": error.get("filename"),
                    "line": error.get("location", {}).get("row"),
                    "column": error.get("location", {}).get("column"),
                    "code": error.get("code"),
                    "message": error.get("message"),
                    "fix_available": error.get("fix") is not None
                }
                f.write(json.dumps(entry) + "\n")

        # Write summary
        summary = {
            "type": "summary",
            "timestamp": timestamp,
            "syntax_passed": results.get("syntax", {}).get("passed", 0),
            "syntax_failed": results.get("syntax", {}).get("failed", 0),
            "lint_errors": results.get("ruff", {}).get("total_errors", 0),
            "error_summary": results.get("ruff", {}).get("summary", {})
        }
        f.write(json.dumps(summary) + "\n")

    print(f"Results written to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Python linting script for packages_py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--path", "-p",
        default=DEFAULT_CONFIG["target_dir"],
        help=f"Target directory to lint (default: {DEFAULT_CONFIG['target_dir']})"
    )

    parser.add_argument(
        "--fix", "-f",
        action="store_true",
        help="Auto-fix fixable errors"
    )

    parser.add_argument(
        "--syntax-only", "-s",
        action="store_true",
        help="Run syntax check only (py_compile)"
    )

    parser.add_argument(
        "--ruff-only", "-r",
        action="store_true",
        help="Run ruff linter only (skip syntax check)"
    )

    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output JSONL file for results"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--ignore",
        default=",".join(DEFAULT_CONFIG["ignored_rules"]),
        help=f"Comma-separated list of rules to ignore (default: {','.join(DEFAULT_CONFIG['ignored_rules'])})"
    )

    parser.add_argument(
        "--no-ignore",
        action="store_true",
        help="Don't ignore any rules"
    )

    args = parser.parse_args()

    # Parse ignored rules
    ignored_rules = [] if args.no_ignore else args.ignore.split(",")

    print("=" * 60)
    print("Python Linting Script")
    print("=" * 60)
    print(f"Target: {args.path}")
    print(f"Auto-fix: {'enabled' if args.fix else 'disabled'}")
    print(f"Ignored rules: {', '.join(ignored_rules) if ignored_rules else 'none'}")
    print()

    results = {}
    exit_code = 0

    # Find Python files
    python_files = find_python_files(args.path, DEFAULT_CONFIG["exclude_patterns"])
    print(f"Found {len(python_files)} Python files")
    print()

    if len(python_files) == 0:
        print("No Python files found to lint.")
        return 0

    # Run syntax check
    if not args.ruff_only:
        print("-" * 40)
        print("Syntax Check (py_compile)")
        print("-" * 40)

        syntax_results = run_syntax_check(python_files, args.verbose)
        results["syntax"] = syntax_results

        print(f"\nSyntax check: {syntax_results['passed']}/{syntax_results['total']} passed")

        if syntax_results["failed"] > 0:
            exit_code = 1
            print(f"  {syntax_results['failed']} files with syntax errors")
        print()

    # Run ruff linter
    if not args.syntax_only:
        print("-" * 40)
        print(f"Ruff Linter {'(with --fix)' if args.fix else ''}")
        print("-" * 40)

        ruff_results = run_ruff_check(
            args.path,
            ignored_rules,
            fix=args.fix,
            verbose=args.verbose
        )
        results["ruff"] = ruff_results

        if ruff_results["total_errors"] == 0:
            print("\nAll checks passed!")
        else:
            exit_code = 1
            print(f"\nFound {ruff_results['total_errors']} errors")

            # Show summary by error code
            if ruff_results["summary"]:
                print("\nErrors by code:")
                for code, count in sorted(ruff_results["summary"].items()):
                    print(f"  {code}: {count}")

            # Show first 10 errors in verbose mode
            if args.verbose and ruff_results["errors"]:
                print("\nFirst 10 errors:")
                for error in ruff_results["errors"][:10]:
                    print(f"  {format_ruff_error(error)}")

                if len(ruff_results["errors"]) > 10:
                    print(f"  ... and {len(ruff_results['errors']) - 10} more")
        print()

    # Write output file
    if args.output:
        write_jsonl_output(results, args.output)

    # Final summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    if "syntax" in results:
        status = "PASS" if results["syntax"]["failed"] == 0 else "FAIL"
        print(f"Syntax:  [{status}] {results['syntax']['passed']}/{results['syntax']['total']} files OK")

    if "ruff" in results:
        status = "PASS" if results["ruff"]["total_errors"] == 0 else "FAIL"
        print(f"Ruff:    [{status}] {results['ruff']['total_errors']} errors")

    print()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
