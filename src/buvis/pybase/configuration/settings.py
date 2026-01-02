"""Base settings models for tool-specific configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ToolSettings(BaseModel):
    """Base for tool-specific settings.

    All tool namespaces inherit from this. Each tool gets enabled: bool = True.
    Subclasses add tool-specific fields. Uses BaseModel (not BaseSettings) since
    parent GlobalSettings handles ENV resolution.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = True
