from fastapi import FastAPI, Request


def mount(app: FastAPI):
    """
    Mount overwrite-from-context health check routes to the FastAPI application.
    This function is called by the server bootstrap process.
    """

    @app.get("/healthz/admin/overwrite-from-context/status")
    async def overwrite_from_context_status(request: Request):
        """Return the initialization status of the overwrite-from-context resolver."""
        try:
            registry = getattr(request.app.state, "_context_registry", None)
            if registry is None:
                return {
                    "initialized": False,
                    "error": "Context resolver not configured",
                }
            return {
                "initialized": True,
                "registered_functions": registry.list(),
            }
        except Exception as e:
            return {
                "initialized": False,
                "error": str(e),
            }

    @app.get("/healthz/admin/overwrite-from-context/json")
    async def overwrite_from_context_json(request: Request):
        """Return the full configuration as JSON for debugging."""
        try:
            registry = getattr(request.app.state, "_context_registry", None)
            resolver = getattr(request.app.state, "_context_resolver", None)
            raw_config = getattr(request.app.state, "_context_raw_config", None)
            resolved_config = getattr(request.app.state, "resolved_config", None)

            if registry is None:
                return {
                    "initialized": False,
                    "error": "Context resolver not configured",
                }

            function_names = registry.list()
            function_scopes = {}
            for name in function_names:
                scope = registry.get_scope(name)
                function_scopes[name] = scope.value if scope else None

            return {
                "initialized": True,
                "config": {
                    "registered_functions": function_names,
                    "function_scopes": function_scopes,
                    "raw_config": raw_config,
                    "resolved_config": resolved_config,
                },
            }
        except Exception as e:
            return {
                "initialized": False,
                "error": str(e),
            }

    @app.get("/healthz/admin/overwrite-from-context/keys")
    async def overwrite_from_context_keys(request: Request):
        """Return only the top-level keys from the configuration (no values)."""
        try:
            registry = getattr(request.app.state, "_context_registry", None)

            if registry is None:
                return {
                    "initialized": False,
                    "error": "Context resolver not configured",
                }

            return {
                "initialized": True,
                "registered_functions": registry.list(),
            }
        except Exception as e:
            return {
                "initialized": False,
                "error": str(e),
            }
