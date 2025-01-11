from typing import Any
from app.models.group_model import Group
from app.models.user_model import User
from app.schemas.group_schema import IGroupCreate, IGroupUpdate
from app.crud.base_crud import CRUDBase
from uuid import UUID


class CRUDGroup(CRUDBase[Group, IGroupCreate, IGroupUpdate]):
    async def get_group_by_name(
        self, *, name: str, db_session: Any = None
    ) -> Group:
        return await Group.nodes.get_or_none(name=name)

    async def add_user_to_group(self, *, user: User, group_id: UUID) -> Group:
        group = await super().get(uid=group_id)
        if group:
            await group.users.connect(user)
        return group

    async def add_users_to_group(
        self,
        *,
        users: list[User],
        group_id: UUID,
        db_session: Any = None,
    ) -> Group:
        group = await super().get(uid=group_id)
        if group:
            for user in users:
                await group.users.connect(user)
        return group


group = CRUDGroup(Group)
