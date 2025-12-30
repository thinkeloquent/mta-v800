from fastapi import FastAPI

def mount(app: FastAPI):
    """
    Mount routes to the FastAPI application.
    This function is called by the server bootstrap process.
    """
    @app.get("/")
    async def home():
        return {"message": "Hello from autoloaded route!", "framework": "fastapi"}
