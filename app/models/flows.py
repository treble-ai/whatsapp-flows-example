from typing import Any, Literal

from pydantic import BaseModel, RootModel


class FlowRequest(BaseModel):
    encrypted_flow_data: str
    encrypted_aes_key: str
    initial_vector: str


# Base class for all flow messages
class FlowData(BaseModel):
    version: str

    class Config:
        extra = "allow"  # Allow extra fields for forward compatibility


# Specific message types
class FlowPing(FlowData):
    action: Literal["ping"]


class FlowDataExchange(FlowData):
    action: Literal["data_exchange", "INIT", "BACK"]
    screen: str
    data: dict[str, Any]
    flow_token: str


class GenericFlowMessage(RootModel[dict[str, Any]]):
    """Generic model to parse any flow message based on the 'action' field"""

    root: dict[str, Any]

    def get_specific_model(self) -> FlowPing | FlowDataExchange:
        """Convert the generic message to a specific model based on action"""
        data = self.root
        action = data.get("action")
        print(f"Action: {action}, Data: {data}")
        if action == "ping":
            return FlowPing(**data)
        elif action in ("data_exchange", "INIT", "BACK"):
            return FlowDataExchange(**data)
        else:
            raise ValueError(f"Unknown action: {action}")


def parse_flow_message(decrypted_data: dict[str, Any]) -> FlowPing | FlowDataExchange:
    """Parse decrypted data into appropriate flow message model"""
    generic = GenericFlowMessage(root=decrypted_data)
    return generic.get_specific_model()
