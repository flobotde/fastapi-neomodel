from app.schemas.media_schema import IMediaCreate
from app.schemas.user_schema import IUserCreate, IUserUpdate
from app.models.user_model import User
from app.models.media_model import Media
from app.models.image_media_model import ImageMedia
from app.core.security import verify_password, get_password_hash
from pydantic.networks import EmailStr
from typing import Any
from app.crud.base_crud import CRUDBase
from app.crud.user_follow_crud import user_follow as UserFollowCRUD
from uuid import UUID
from neomodel.exceptions import DoesNotExist


class CRUDUser(CRUDBase[User, IUserCreate, IUserUpdate]):
    async def get_by_email(
        self, *, email: str, db_session: Any = None
    ) -> User | None:
        try:
            return await User.nodes.get(email=email)
        except DoesNotExist:
            return None

    async def get_by_id_active(self, *, id: UUID) -> User | None:
        user = await super().get(uid=id)
        if not user or not user.is_active:
            return None
        return user

    async def create_with_role(
        self, *, obj_in: IUserCreate, db_session: Any = None
    ) -> User:
        db_obj = User.from_orm(obj_in)
        db_obj.hashed_password = get_password_hash(obj_in.password)
        await db_obj.save()
        return db_obj

    async def update_is_active(
        self, *, db_obj: list[User], obj_in: int | str | dict[str, Any]
    ) -> list[User]:
        updated_users = []
        for user in db_obj:
            user.is_active = obj_in.is_active
            await user.save()
            updated_users.append(user)
        return updated_users

    async def authenticate(self, *, email: EmailStr, password: str) -> User | None:
        user = await self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_photo(
        self,
        *,
        user: User,
        image: IMediaCreate,
        heigth: int,
        width: int,
        file_format: str,
    ) -> User:
        image_media = ImageMedia(
            media=Media.from_orm(image),
            height=heigth,
            width=width,
            file_format=file_format,
        )
        await image_media.save()
        user.image.connect(image_media)
        await user.save()
        return user

    async def remove(
        self, *, id: UUID | str, db_session: Any = None
    ) -> User:
        user = await self.get(uid=id)
        if not user:
            raise DoesNotExist("User not found")

        # Handle follow relationships
        followings = await user.following.all()
        for following in followings:
            target_user = await following.followers.get()
            target_user.follower_count -= 1
            await target_user.save()
            await user.following.disconnect(following)

        followers = await user.followers.all()
        for follower in followers:
            source_user = await follower.following.get()
            source_user.following_count -= 1
            await source_user.save()
            await user.followers.disconnect(follower)

        await user.delete()
        return user


user = CRUDUser(User)
