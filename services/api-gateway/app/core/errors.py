from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.schemas.common import ErrorResponse


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        first_error = exc.errors()[0] if exc.errors() else {"msg": "Validation failed"}
        payload = ErrorResponse(
            error={"code": "VALIDATION_ERROR", "message": str(first_error.get("msg", "Validation failed"))}
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def generic_exception_handler(_: Request, __: Exception) -> JSONResponse:
        payload = ErrorResponse(error={"code": "INTERNAL_ERROR", "message": "Unexpected server error"})
        return JSONResponse(status_code=500, content=payload.model_dump())
