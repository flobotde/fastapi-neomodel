from uuid import UUID
from typing import Any
from app.crud.base_crud import CRUDBase
from app.models.user_follow_model import UserFollow as UserFollowModel
from app.models.user_model import User
from app.schemas.user_follow_schema import IUserFollowCreate, IUserFollowUpdate
from neomodel.exceptions import DoesNotExist


class CRUDUserFollow(CRUDBase[UserFollowModel, IUserFollowCreate, IUserFollowUpdate]):
    async def follow_a_user_by_target_user_id(
        self,
        *,
        user: User,
        target_user: User,
        db_session: Any = None,
    ) -> UserFollowModel:
        # Create the follow relationship
        follow_rel = await user.following.connect(target_user)
        
        # Check for mutual follow
        if await target_user.following.is_connected(user):
            follow_rel.is_mutual = True
            # Update the reverse relationship
            reverse_rel = await target_user.following.relationship(user)
            reverse_rel.is_mutual = True
            await reverse_rel.save()
        
        await follow_rel.save()
        
        # Update counts
        user.following_count += 1
        target_user.follower_count += 1
        await user.save()
        await target_user.save()
        
        return follow_rel

    async def unfollow_a_user_by_id(
        self,
        *,
        user_follow_id: UUID,
        user: User,
        target_user: User,
        db_session: Any = None,
    ) -> UserFollowModel:
        # Get the relationship
        follow_rel = await user.following.relationship(target_user)
        
        # Check for mutual follow
        if await target_user.following.is_connected(user):
            # Update the reverse relationship
            reverse_rel = await target_user.following.relationship(user)
            reverse_rel.is_mutual = False
            await reverse_rel.save()
        
        # Disconnect the follow relationship
        await user.following.disconnect(target_user)
        
        # Update counts
        user.following_count -= 1
        target_user.follower_count -= 1
        await user.save()
        await target_user.save()
        
        return follow_rel

    async def get_follow_by_user_id(
        self, *, user_id: UUID, db_session: Any = None
    ) -> list[UserFollowModel] | None:
        user = await User.nodes.get(uid=user_id)
        return await user.following.all_relationships()

    async def get_follow_by_target_user_id(
        self, *, target_user_id: UUID, db_session: Any = None
    ) -> list[UserFollowModel] | None:
        target_user = await User.nodes.get(uid=target_user_id)
        return await target_user.followers.all_relationships()

    async def get_follow_by_user_id_and_target_user_id(
        self,
        *,
        user_id: UUID,
        target_user_id: UUID,
        db_session: Any = None,
    ) -> UserFollowModel | None:
        try:
            user = await User.nodes.get(uid=user_id)
            target_user = await User.nodes.get(uid=target_user_id)
            return await user.following.relationship(target_user)
        except DoesNotExist:
            return None


user_follow = CRUDUserFollow(UserFollowModel)
