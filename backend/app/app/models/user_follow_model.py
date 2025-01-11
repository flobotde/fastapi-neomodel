from datetime import datetime
from neomodel import (
    BooleanProperty,
    DateTimeProperty,
    StructuredRel
)


class UserFollowRel(StructuredRel):
    """Model for relationship properties between users"""
    is_mutual = BooleanProperty(default=False)
    followed_at = DateTimeProperty(
        default=lambda: datetime.now(datetime.timezone.utc)
    )
