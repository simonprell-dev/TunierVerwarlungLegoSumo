from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., examples=["VALIDATION_ERROR"])
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    service: str


class VersionResponse(BaseModel):
    service: str
    version: str
    api_version: str
