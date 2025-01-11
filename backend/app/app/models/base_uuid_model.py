from app.utils.uuid6 import uuid7, UUID
from neomodel import AsyncStructuredNode, DateTimeProperty, UniqueIdProperty
from datetime import datetime

class BaseUUIDModel(AsyncStructuredNode):
    uid = UniqueIdProperty(default=uuid7, primary_key=True)
    updated_at = DateTimeProperty(default=lambda: datetime.now(datetime.timezone.utc))
    created_at = DateTimeProperty(default=lambda: datetime.now(datetime.timezone.utc))
