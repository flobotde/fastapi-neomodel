from datetime import datetime
from neomodel import (
    DateTimeProperty,
    StructuredRel
)
class LinkGroupUser(StructuredRel):
    member_since = DateTimeProperty(
        default=lambda: datetime.now(datetime.timezone.utc)
    )
