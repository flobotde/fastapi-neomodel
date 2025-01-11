from app.models.base_uuid_model import BaseUUIDModel
from neomodel import StringProperty, RelationshipFrom

class GroupBase(BaseUUIDModel):
    name = StringProperty(required=True, unique_index=True)
    description = StringProperty()
    
class Group(GroupBase):
    created_by = RelationshipFrom("User", "CREATED_BY")
