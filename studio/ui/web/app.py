from __future__ import annotations

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
except ModuleNotFoundError:  # pragma: no cover - optional runtime adapter
    app = None
else:
    from studio.ui.web.server import INDEX, api_approve, api_create_project, api_generate, api_register_asset, api_review, api_status

    app = FastAPI(title="Studio v2")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return INDEX

    @app.get("/api/status")
    def status(root: str) -> dict:
        return api_status(root)

    @app.post("/api/create-project")
    def create_project(payload: dict) -> dict:
        return api_create_project(payload)

    @app.post("/api/register-asset")
    def register_asset(payload: dict) -> dict:
        return api_register_asset(payload)

    @app.post("/api/approve")
    def approve(payload: dict) -> dict:
        return api_approve(payload)

    @app.post("/api/generate")
    def generate(payload: dict) -> dict:
        return api_generate(payload)

    @app.post("/api/review")
    def review(payload: dict) -> dict:
        return api_review(payload)
