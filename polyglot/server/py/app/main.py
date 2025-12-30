import asyncio
import os
from fastapi import Request
from server import init, start
from logger import logger

log = logger.create("main", __file__)

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

log.info("Initializing application", {"title": config["title"]})
server = init(config)

log.debug("Registering routes")


@server.get("/")
async def root(request: Request):
    log.trace("Request received", {"path": "/", "method": "GET"})
    return {
        "status": "ok",
        "state": {
            "user": getattr(request.state, "user", None),
            "role": getattr(request.state, "role", None)
        }
    }


@server.get("/health")
async def health(request: Request):
    log.trace("Health check request", {"path": "/health", "method": "GET"})
    return {
        "status": "ok",
        "state": {
            "user": getattr(request.state, "user", None),
            "role": getattr(request.state, "role", None)
        }
    }


log.info("Routes registered", {"routes": ["/", "/health"]})


async def main():
    log.info("Starting server", {"host": config["host"], "port": config["port"]})
    await start(server, config)


if __name__ == "__main__":
    asyncio.run(main())
