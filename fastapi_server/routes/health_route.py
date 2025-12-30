from fastapi import FastAPI

def mount(app: FastAPI):
    """
    Mount routes to the FastAPI application.
    This function is called by the server bootstrap process.
    """
    @app.get("/health")
    async def health():
        return {"message": "Hello from autoloaded route!", "framework": "fastapi"}
