from pydantic import BaseModel, ConfigDict


class ServiceResponse(BaseModel):
    """Safe public catalogue representation; no internal database fields leak."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str
