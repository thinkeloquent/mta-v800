import asyncio
import os
from fastapi import Request
from server import init, start

config = {
    "title": "My API",
    "host": "0.0.0.0",
    "port": 3000,
    "bootstrap": {
        "load_env": "./config/env",
        "lifecycle": "./config/lifecycle"
    },
    "initial_state": {
        "user": "anonymous",
        "role": "guest"
    }
}

server = init(config)

@server.get("/")
async def health(request: Request):
    return {
        "status": "ok", 
        "state": {
            "user": getattr(request.state, "user", None),
            "role": getattr(request.state, "role", None)
        }
    }

@server.get("/health")
async def health(request: Request):
    return {
        "status": "ok", 
        "state": {
            "user": getattr(request.state, "user", None),
            "role": getattr(request.state, "role", None)
        }
    }


async def main():

    print(f"Starting server on {config['host']}:{config['port']}...")
    await start(server, config)

if __name__ == "__main__":
    asyncio.run(main())
