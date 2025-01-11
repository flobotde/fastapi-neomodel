from app.utils.uuid6 import uuid7, UUID
from .media_model import Media
from app.models.base_uuid_model import BaseUUIDModel
from neomodel import StringProperty, IntProperty, UniqueIdProperty, RelationshipTo

class ImageMediaBase(BaseUUIDModel):
    file_format = StringProperty(default=None)
    width = IntProperty(default=None)
    height = IntProperty(default=None)


class ImageMedia(ImageMediaBase):
    media_id = UniqueIdProperty(default=uuid7)
    media = RelationshipTo('Media', 'HAS_MEDIA')
