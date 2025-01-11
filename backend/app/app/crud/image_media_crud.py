from typing import Any
from uuid import UUID
from app.crud.base_crud import CRUDBase
from app.models.image_media_model import ImageMedia
from app.models.user_model import User
from app.schemas.image_media_schema import IImageMediaCreate, IImageMediaUpdate


class CRUDImageMedia(CRUDBase[ImageMedia, IImageMediaCreate, IImageMediaUpdate]):
    async def get_by_path(
        self, *, path: str, db_session: Any = None
    ) -> ImageMedia | None:
        return await ImageMedia.nodes.get_or_none(path=path)

    async def get_by_user(
        self, *, user_id: UUID, db_session: Any = None
    ) -> ImageMedia | None:
        user = await User.nodes.get_or_none(uid=user_id)
        if user:
            return await user.image.single()
        return None

    async def create_with_user(
        self, *, obj_in: IImageMediaCreate, user_id: UUID, db_session: Any = None
    ) -> ImageMedia:
        image = ImageMedia(**obj_in.dict())
        await image.save()
        user = await User.nodes.get_or_none(uid=user_id)
        if user:
            await user.image.connect(image)
        return image

    async def update_image(
        self, *, obj_current: ImageMedia, obj_new: IImageMediaUpdate | dict[str, Any]
    ) -> ImageMedia:
        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(obj_current, field, value)
        await obj_current.save()
        return obj_current
      

image = CRUDImageMedia(ImageMedia)
