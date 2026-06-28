from fastapi import APIRouter
import httpx

router = APIRouter()

@router.get("/github/repos")
async def get_repos(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
        )
    return response.json()

@router.get("/github/commits")
async def get_commits(repo: str, token: str, since: str, until: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{repo}/commits",
            params={
                "since": f"{since}T00:00:00Z",
                "until": f"{until}T23:59:59Z"
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
        )
    return response.json()

@router.get("/github/all-diffs")
async def get_all_diffs(repo: str, token: str, since: str, until: str):
    async with httpx.AsyncClient() as client:
        commits_response = await client.get(
            f"https://api.github.com/repos/{repo}/commits",
            params={
                "since": f"{since}T00:00:00Z",
                "until": f"{until}T23:59:59Z"
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
        )
        commits = commits_response.json()
        all_diffs = []

        for commit in commits:
            sha = commit["sha"]
            diff_response = await client.get(
                f"https://api.github.com/repos/{repo}/commits/{sha}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json"
                }
            )
            diff_data = diff_response.json()
            all_diffs.append({
                "sha": sha,
                "message": commit["commit"]["message"],
                "files": diff_data.get("files", [])
            })

        return all_diffs