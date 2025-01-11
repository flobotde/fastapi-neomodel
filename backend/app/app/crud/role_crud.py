from typing import Any
from app.schemas.role_schema import IRoleCreate, IRoleUpdate
from app.models.role_model import Role
from app.models.user_model import User
from app.crud.base_crud import CRUDBase
from uuid import UUID


class CRUDRole(CRUDBase[Role, IRoleCreate, IRoleUpdate]):
    async def get_role_by_name(
        self, *, name: str, db_session: Any = None
    ) -> Role:
        return await Role.nodes.get_or_none(name=name)

    async def add_role_to_user(self, *, user: User, role_id: UUID) -> Role:
        role = await super().get(uid=role_id)
        if role:
            await role.users.connect(user)
        return role


role = CRUDRole(Role)
