from fastapi import APIRouter
from dotenv import load_dotenv
import os
import httpx

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

router = APIRouter()

@router.get("/auth/github/login")
def github_login():
    client_id = os.getenv("GITHUB_CLIENT_ID")
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=repo"
    return {"url": github_auth_url}

@router.get("/auth/github/callback")
async def github_callback(code: str):
    client_id = os.getenv("GITHUB_CLIENT_ID")
    client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code
            },
            headers={"Accept": "application/json"}
        )
    
    data = response.json()
    access_token = data.get("access_token")
    return {"access_token": access_token}