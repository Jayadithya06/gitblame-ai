import httpx
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2"

async def analyze_suspects(bug_description: str, suspects: list):
    prompt = build_prompt(bug_description, suspects)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
    
    data = response.json()
    raw_text = data["response"]
    
    try:
        result = json.loads(raw_text)
    except:
        result = {"raw": raw_text}
    
    return result

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

Return ONLY the JSON array, no other text."""