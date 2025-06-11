from fastapi import FastAPI
from api.endpoints import transcription, gemini, auth
from middlewares.auth_middleware import AuthMiddleware
from fastapi.staticfiles import StaticFiles
from configs.api_config import API_PREFIX
from fastapi.openapi.utils import get_openapi
import uvicorn
import os
app = FastAPI(title="Englisious API", version="1.0.0")

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    # Apply BearerAuth to all routes except /auth
    for path in openapi_schema["paths"]:
        if not path.startswith("/auth"):
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
        else:
            # Ensure /auth routes do not require authentication
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = []

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Include routers

app.add_middleware(AuthMiddleware)

app.include_router(transcription.router, prefix=API_PREFIX, tags=["transcription"])
app.include_router(gemini.router, prefix=API_PREFIX, tags=["chat_box"])
app.include_router(auth.router, prefix='/auth', tags=["auth"])

# Mount the 'audio' directory to serve static files
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")  
    port = int(os.getenv("FASTAPI_PORT", 8000)) 
    uvicorn.run(app, host=host, port=port)

