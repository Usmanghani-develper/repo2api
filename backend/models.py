"""Pydantic models for request/response validation."""

from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class FunctionParameter(BaseModel):
    """Model for function parameter information."""
    
    name: str = Field(..., description="Parameter name")
    type: str = Field(default="any", description="Parameter type")
    default: Optional[Any] = Field(default=None, description="Default value")
    is_optional: bool = Field(default=False, description="Whether parameter is optional")
    description: Optional[str] = Field(default=None, description="Parameter description")


class FunctionInfo(BaseModel):
    """Model for detected function information."""
    
    name: str = Field(..., description="Function name")
    module: str = Field(..., description="Module path")
    file_path: str = Field(..., description="File path")
    docstring: Optional[str] = Field(default=None, description="Function docstring")
    parameters: List[FunctionParameter] = Field(default_factory=list, description="Function parameters")
    return_type: str = Field(default="any", description="Return type")
    is_async: bool = Field(default=False, description="Whether function is async")
    line_number: int = Field(..., description="Line number in source file")


class RepositoryAnalysis(BaseModel):
    """Model for repository analysis results."""
    
    repository_url: Optional[str] = Field(default=None, description="Repository URL")
    repository_name: str = Field(..., description="Repository name")
    total_functions: int = Field(..., description="Total functions detected")
    functions: List[FunctionInfo] = Field(default_factory=list, description="Detected functions")
    analysis_timestamp: str = Field(..., description="When analysis was performed")
    language: str = Field(default="python", description="Primary language")
    errors: List[str] = Field(default_factory=list, description="Any errors during analysis")


class APIEndpoint(BaseModel):
    """Model for auto-generated API endpoint."""
    
    path: str = Field(..., description="API endpoint path")
    method: str = Field(default="POST", description="HTTP method")
    function_name: str = Field(..., description="Original function name")
    parameters: List[FunctionParameter] = Field(default_factory=list, description="Endpoint parameters")
    return_type: str = Field(default="any", description="Expected return type")
    description: Optional[str] = Field(default=None, description="Endpoint description")
    tags: List[str] = Field(default_factory=list, description="Endpoint tags")


class APIResponse(BaseModel):
    """Model for successful API response."""
    
    success: bool = Field(default=True, description="Whether request was successful")
    data: Dict[str, Any] = Field(..., description="Response data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    timestamp: str = Field(..., description="Response timestamp")


class ErrorResponse(BaseModel):
    """Model for error API response."""
    
    success: bool = Field(default=False, description="Whether request was successful")
    error: str = Field(..., description="Error message")
    error_type: str = Field(default="error", description="Error type")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: str = Field(..., description="Error timestamp")
    traceback: Optional[str] = Field(default=None, description="Error traceback (debug only)")


class GenerateAPIRequest(BaseModel):
    """Model for API generation request."""
    
    repository_url: Optional[str] = Field(default=None, description="GitHub repository URL")
    repository_path: Optional[str] = Field(default=None, description="Local repository path")
    language: str = Field(default="python", description="Programming language")
    auto_start: bool = Field(default=False, description="Whether to auto-start the API")


class ServeAPIRequest(BaseModel):
    """Model for API serve request."""
    
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on changes")
    enable_auth: bool = Field(default=False, description="Enable API key authentication")
    enable_rate_limit: bool = Field(default=False, description="Enable rate limiting")


class EndpointRequest(BaseModel):
    """Model for generic endpoint request with parameters."""
    
    class Config:
        extra = "allow"  # Allow extra fields for dynamic parameters


class HealthCheck(BaseModel):
    """Model for health check response."""
    
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    loaded_endpoints: int = Field(default=0, description="Number of loaded endpoints")
    available_languages: List[str] = Field(default_factory=list, description="Supported languages")
