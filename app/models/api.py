from pydantic import BaseModel


class OKResponse(BaseModel):
    message: str = "ok"
