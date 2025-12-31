from fastapi import FastAPI, Request

def mount(app: FastAPI):
    """
    Mount routes to the FastAPI application.
    This function is called by the server bootstrap process.
    """
    @app.get("/health")
    async def health(request: Request):
        build_id = getattr(getattr(request.state, "build_info", None), "id", None) if hasattr(request.state, "build_info") else None
        if not build_id or not build_id.strip():
            build_id = "no build id found"
        return {"message": "Hello from autoloaded route!", "framework": "fastapi", "build_id": build_id}
