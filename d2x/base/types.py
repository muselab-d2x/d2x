from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
from rich.console import Console


class OutputFormat(str, Enum):
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"
    MARKDOWN = "markdown"


# Redefine DebugModeType as bool
OutputFormatType = OutputFormat
DebugModeType = bool


class CLIOptions(BaseModel):
    """Model to encapsulate CLI options."""

    output_format: OutputFormatType = Field(
        default=OutputFormat.TEXT, description="Output format for CLI commands."
    )
    debug: DebugModeType = Field(
        default=False, description="Enable or disable debug mode."
    )
    console: Console = Field(
        default_factory=Console, description="Rich Console for output."
    )

    class Config:
        arbitrary_types_allowed = True


# Add other enums and types as needed
