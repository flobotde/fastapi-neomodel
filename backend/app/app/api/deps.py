from typing import Callable
from fastapi import Depends, HTTPException, status
from app.utils.token import get_valid_tokens
from app.utils.minio_client import MinioClient
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from app.models.user_model import User
from app.models.role_model import Role
from pydantic import ValidationError
from app.core import security
from app.core.config import settings
from app.schemas.common_schema import IMetaGeneral, TokenType
import redis.asyncio as aioredis
from redis.asyncio import Redis
from neomodel import db


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_redis_client() -> Redis:
    redis = await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )
    return redis


async def get_general_meta() -> IMetaGeneral:
    current_roles = await Role.nodes.all()
    return IMetaGeneral(roles=current_roles)


def get_current_user(required_roles: list[str] = None) -> Callable[[], User]:
    async def current_user(
        token: str = Depends(reusable_oauth2),
        redis_client: Redis = Depends(get_redis_client),
    ) -> User:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user_id = payload["sub"]
        valid_access_tokens = await get_valid_tokens(
            redis_client, user_id, TokenType.ACCESS
        )
        if valid_access_tokens and token not in valid_access_tokens:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user = await User.nodes.get_or_none(uid=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        if required_roles:
            is_valid_role = False
            role = await user.role.single()
            if role and role.name in required_roles:
                is_valid_role = True

            if not is_valid_role:
                raise HTTPException(
                    status_code=403,
                    detail=f"""Role "{required_roles}" is required for this action""",
                )

        return user

    return current_user


def minio_auth() -> MinioClient:
    minio_client = MinioClient(
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        bucket_name=settings.MINIO_BUCKET,
        minio_url=settings.MINIO_URL,
    )
    return minio_client
