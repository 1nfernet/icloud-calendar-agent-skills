#!/usr/bin/env python3
"""Validate the public skill package without accessing user accounts."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("apple-calendar-followup", "icloud-calendar-write")


def validate():
    problems = []
    for name in SKILLS:
        for filename in ("SKILL.md", "SKILL.en.md"):
            entry = ROOT / "skills" / name / filename
            if not entry.is_file():
                problems.append(f"Missing skill entry: {name}/{filename}")
                continue
            content = entry.read_text(encoding="utf-8")
            metadata = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
            if metadata is None:
                problems.append(f"Missing frontmatter: {name}/{filename}")
                continue
            if f"name: {name}" not in metadata[1].splitlines():
                problems.append(f"Skill name mismatch: {name}/{filename}")
            if not re.search(r"^description:\s*\S", metadata[1], re.MULTILINE):
                problems.append(f"Missing description: {name}/{filename}")
            if "[TODO:" in content:
                problems.append(f"Unfinished skill: {name}/{filename}")

    if not (ROOT / "README.en.md").is_file():
        problems.append("Missing English README")
    for source in (ROOT / "skills").rglob("*.md"):
        if source.name.endswith(".en.md"):
            continue
        translated = source.with_name(source.stem + ".en.md")
        if not translated.is_file():
            problems.append(f"Missing English counterpart: {source.relative_to(ROOT)}")

    defaults_path = ROOT / "skills/apple-calendar-followup/assets/default-config.json"
    try:
        defaults = json.loads(defaults_path.read_text(encoding="utf-8"))
        if defaults.get("calendar") != {"provider": "icloud", "access": "mac_calendar"}:
            problems.append("Public defaults must not contain a calendar binding")
        if defaults.get("mail") != {"provider": "gmail", "cc": [], "bcc": []}:
            problems.append("Public defaults must not contain sender/recipient bindings")
    except (OSError, ValueError) as exc:
        problems.append(f"Invalid default configuration: {type(exc).__name__}")

    email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
    home_path = re.compile(r"/(?:Users|home)/[^\s/<>]+")
    secret_pattern = re.compile(
        r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
        r"|sk-(?:proj-)?[A-Za-z0-9_-]{25,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
    )
    forbidden_suffixes = {".ics", ".db", ".sqlite", ".sqlite3", ".zip", ".log"}
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts or "__pycache__" in relative.parts or not path.is_file():
            continue
        if path.name in {"config.json", ".env"} or path.suffix in forbidden_suffixes:
            problems.append(f"Runtime artifact in public package: {relative}")
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeError:
            problems.append(f"Unexpected binary file: {relative}")
            continue
        if home_path.search(content):
            problems.append(f"Personal home path in: {relative}")
        if secret_pattern.search(content):
            problems.append(f"Potential credential in: {relative}")
        for match in email_pattern.finditer(content):
            domain = match[1].lower()
            if domain not in {"example.com", "example.org", "example.net", "example.invalid"}:
                problems.append(f"Non-example email address in: {relative}")
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", content):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (path.parent / target.split("#", 1)[0]).resolve()
                try:
                    resolved.relative_to(ROOT)
                except ValueError:
                    problems.append(f"Link leaves public package: {relative}")
                    continue
                if not resolved.exists():
                    problems.append(f"Broken local link in {relative}: {target}")

    return sorted(set(problems))


if __name__ == "__main__":
    failures = validate()
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        sys.exit(1)
    print("Skill structure, links, public defaults and privacy checks passed.")
