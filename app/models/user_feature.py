from typing import Literal
from uuid import UUID

from app.models.db import DBBase


class UserFeature(DBBase):
    user_id: UUID
    type: Literal["AI_NODE", "META_ADS", "HUBSPOT_SIDE_PANEL", "HUBSPOT_CUSTOM_EVENTS", "DYNAMIC_WHATSAPP_FLOWS"]
