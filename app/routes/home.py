from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

home_route = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@home_route.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "full_page": True,
            "body_class": "landing-body",
        },
    )