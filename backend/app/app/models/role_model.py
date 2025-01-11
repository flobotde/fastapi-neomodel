from app.models.base_uuid_model import BaseUUIDModel
from neomodel import (
    StringProperty,
)
from pydantic import BaseModel
class RoleBase(BaseModel):
    name: str
    description: str

class Role(BaseUUIDModel, RoleBase):
    pass