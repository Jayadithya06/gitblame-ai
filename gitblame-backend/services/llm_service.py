import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

USE_LOCAL = os.getenv("USE_LOCAL_EMBEDDINGS", "true").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def build_prompt(bug_description: str, suspects: list):
    suspects_text = ""
    for i, suspect in enumerate(suspects):
        metadata = suspect.get("metadata", {})
        suspects_text += f"""
SUSPECT {i + 1}:
Commit SHA: {metadata.get('sha', 'unknown')}
Commit Message: {metadata.get('message', 'unknown')}
File Changed: {metadata.get('filename', 'unknown')}
Diff: {suspect.get('document', '')}
---
"""
    return f"""You are a senior software engineer debugging a production issue.

BUG DESCRIPTION:
{bug_description}

TOP SUSPECT COMMITS (ranked by semantic similarity to the bug):
{suspects_text}

Analyze each suspect commit and return a JSON array with this exact structure:
[
  {{
    "sha": "commit sha here",
    "message": "commit message here",
    "filename": "file changed here",
    "confidence": 85,
    "explanation": "Plain English explanation of why this commit is suspicious",
    "suspicious_lines": "The specific lines most likely to have caused the issue",
    "rollback_command": "git revert <sha>",
    "fix_suggestion": "Specific code fix suggestion to properly resolve the issue"
  }}
]

Return ONLY the JSON array, no other text, no markdown backticks."""

async def analyze_suspects(bug_description: str, suspects: list):
    prompt = build_prompt(bug_description, suspects)

    if USE_LOCAL:
        import httpx
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                }
            )
        data = response.json()
        raw_text = data["response"]
    else:
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.1
        )
        raw_text = chat_completion.choices[0].message.content

    try:
        clean = raw_text.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        result = json.loads(clean.strip())
    except:
        result = {"raw": raw_text}

    return result