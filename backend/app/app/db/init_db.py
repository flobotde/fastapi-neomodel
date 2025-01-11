from app import crud
from app.schemas.role_schema import IRoleCreate
from app.core.config import settings
from app.schemas.user_schema import IUserCreate
from app.schemas.group_schema import IGroupCreate
from app.db import get_db

roles: list[IRoleCreate] = [
    IRoleCreate(name="admin", description="This the Admin role"),
    IRoleCreate(name="user", description="User role"),
]

groups: list[IGroupCreate] = [
    IGroupCreate(name="Admin", description="This is the Admin group")
]

users: list[dict[str, str | IUserCreate]] = [
    {
        "data": IUserCreate(
            first_name="Admin",
            last_name="FastAPI",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email=settings.FIRST_SUPERUSER_EMAIL,
            is_superuser=True,
        ),
        "role": "admin",
    },
    {
        "data": IUserCreate(
            first_name="User",
            last_name="FastAPI",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email="user-" + settings.FIRST_SUPERUSER_EMAIL,
            is_superuser=False,
        ),
        "role": "user",
    },
]


async def init_db() -> None:
    db = await get_db()
    for role in roles:
        role_current = await crud.role.get_role_by_name(name=role.name)
        if not role_current:
            await crud.role.create(obj_in=role)

    for user in users:
        current_user = await crud.user.get_by_email(email=user["data"].email)
        role = await crud.role.get_role_by_name(name=user["role"])
        if not current_user:
            user["data"].role_id = role.id
            await crud.user.create_with_role(obj_in=user["data"])

    for group in groups:
        current_group = await crud.group.get_group_by_name(name=group.name)
        if not current_group:
            current_user = await crud.user.get_by_email(email=users[0]["data"].email)
            new_group = await crud.group.create(
                obj_in=group, created_by_id=current_user.id
            )
            current_users = [
                await crud.user.get_by_email(email=user["data"].email)
                for user in users
            ]
            await crud.group.add_users_to_group(
                users=current_users, group_id=new_group.id
            )
