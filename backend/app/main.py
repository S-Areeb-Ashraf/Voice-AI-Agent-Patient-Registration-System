from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import patients, vapi_tools, vapi_webhook, calls
from app.utils.logging_config import logger

app = FastAPI(
    title="Care Cloud Voice AI Agent - Patient Registration System API",
    description="Backend API exposing REST endpoints and Vapi integration hooks",
    version="1.0.0"
)

# Configure CORS origins
# origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Custom Exception Handler for RequestValidationError (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        # loc will contain e.g. ('body', 'first_name')
        # Skip the parent location 'body' or 'query' to keep error message readable
        filtered_loc = [str(x) for x in error.get("loc", []) if x not in ("body", "query")]
        loc_str = " -> ".join(filtered_loc) if filtered_loc else "request"
        
        msg = error.get("msg", "Invalid value")
        # Remove internal Pydantic prefix to make it clean
        if msg.startswith("Value error, "):
            msg = msg.replace("Value error, ", "", 1)
        
        errors.append(f"{loc_str}: {msg}")
    
    error_msg = "; ".join(errors)
    logger.warning(f"Request validation failure on {request.method} {request.url.path}: {error_msg}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"data": None, "error": f"Validation failed: {error_msg}"}
    )

# 2. Custom Exception Handler for HTTPExceptions (400, 404, 401, etc.)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": exc.detail}
    )

# 3. Custom Exception Handler for Generic Unhandled Exceptions (500)
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled system exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"data": None, "error": f"Internal Server Error: {str(exc)}"}
    )

# Register API Routers
app.include_router(patients.router)
app.include_router(vapi_tools.router)
app.include_router(vapi_webhook.router)
app.include_router(calls.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Patient Registration System API",
        "documentation": "/docs"
    }
