import os
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

BASE = Path(__file__).resolve().parent
app = FastAPI(title="Bank Back-Office Demo")
templates = Jinja2Templates(directory=str(BASE / "templates"))

MEMBERS = {
    "12345": {"name": "Jane Smith", "status": "Active", "savings_balance": "12,450.50"},
    "67890": {"name": "Robert Lee", "status": "Active", "savings_balance": "3,280.20"},
}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={"demo_error": False},
    )


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, member_id: str = ""):
    if os.getenv("SIMULATE_TRANSIENT_ERROR", "false").lower() == "true" and member_id:
        return templates.TemplateResponse(
            request=request,
            name="search.html",
            context={"demo_error": True, "member_id": member_id},
        )
    member = MEMBERS.get(member_id)
    if not member:
        return templates.TemplateResponse(
            request=request,
            name="search.html",
            context={
                "demo_error": False,
                "not_found": bool(member_id),
                "member_id": member_id,
            },
            status_code=200,
        )
    return RedirectResponse(url=f"/member/{member_id}", status_code=303)


@app.get("/member/{member_id}", response_class=HTMLResponse)
async def member(request: Request, member_id: str):
    data = MEMBERS.get(member_id)
    if not data:
        return templates.TemplateResponse(
            request=request,
            name="search.html",
            context={"not_found": True, "member_id": member_id},
        )
    return templates.TemplateResponse(
        request=request,
        name="member.html",
        context={"member_id": member_id, "member": data},
    )
