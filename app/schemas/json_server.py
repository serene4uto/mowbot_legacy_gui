from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

class ServerInfo(BaseModel):
    op: Literal["serverInfo"] = Field(
        "serverInfo",
        description="The operation type, always fixed as 'serverInfo'"
    )
    name: str = Field(
        ...,
        description="Free-form information about the server which the client may optionally display or use for debugging purposes"
    )
    capabilities: List[
        Literal[
            "clientPublish",
            "parameters",
            "parametersSubscribe",
            "time",
            "services",
            "connectionGraph",
            "assets"
        ]
    ] = Field(
        ...,
        description=(
            "Array of strings informing the client about which optional features are supported. "
            "Valid values: 'clientPublish', 'parameters', 'parametersSubscribe', "
            "'time', 'services', 'connectionGraph', 'assets'."
        )
    )
    supportedEncodings: Optional[List[str]] = Field(
        None,
        description="Array of strings informing the client about which encodings may be used for client-side publishing or service call requests/responses."
    )
    metadata: Optional[Dict[str, str]] = Field(
        None,
        description="Optional map of key-value pairs providing additional metadata about the server"
    )
    sessionId: Optional[str] = Field(
        None,
        description="Optional string allowing the client to understand if the connection is a re-connection or a new server instance (e.g., a timestamp or UUID)."
    )
