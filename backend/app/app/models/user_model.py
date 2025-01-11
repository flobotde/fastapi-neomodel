from app.models.base_uuid_model import BaseUUIDModel
from app.models.image_media_model import ImageMedia
from app.schemas.common_schema import IGenderEnum
from neomodel import (StringProperty, BooleanProperty, DateTimeProperty, 
                     RelationshipTo, RelationshipFrom, EmailProperty)


class UserBase(BaseUUIDModel):
    first_name = StringProperty(required=True)
    last_name = StringProperty(required=True)
    email = EmailProperty(unique_index=True, required=True)
    is_active = BooleanProperty(default=True)
    is_superuser = BooleanProperty(default=False)
    birthdate = DateTimeProperty(default=None)  # birthday with timezone
    phone = StringProperty(default=None)
    gender = StringProperty(choices=dict(IGenderEnum), default=IGenderEnum.other)
    state = StringProperty(default=None)
    country = StringProperty(default=None)
    address = StringProperty(default=None)


class User(UserBase):
    hashed_password = StringProperty(required=True)
    
    # Relationships
    role = RelationshipTo('Role', 'HAS_ROLE')
    groups = RelationshipTo('Group', 'BELONGS_TO')
    image = RelationshipTo(ImageMedia, 'HAS_IMAGE')
    
    # Follow relationships
    followers = RelationshipFrom('User', 'FOLLOWS')
    following = RelationshipTo('User', 'FOLLOWS')
    
    # Count properties
    follower_count = StringProperty(default="0")
    following_count = StringProperty(default="0")
