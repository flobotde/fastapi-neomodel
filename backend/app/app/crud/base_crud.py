from typing import Any, Generic, TypeVar
from uuid import UUID
from fastapi import HTTPException
from pydantic import BaseModel
from neomodel import AsyncStructuredNode
from neomodel.exceptions import DoesNotExist, UniqueProperty
from fastapi_pagination import Params, Page
from app.schemas.common_schema import IOrderEnum

ModelType = TypeVar("ModelType", bound=AsyncStructuredNode)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A neomodel AsyncStructuredNode class
        """
        self.model = model

    async def get(self, *, uid: UUID | str, db_session: Any = None) -> ModelType | None:
        try:
            return await self.model.nodes.get(uid=uid)
        except DoesNotExist:
            return None

    async def get_by_ids(
        self,
        *,
        list_ids: list[UUID | str],
        db_session: Any = None,
    ) -> list[ModelType]:
        return await self.model.nodes.filter(uid__in=list_ids)

    async def get_count(self, db_session: Any = None) -> int:
        return await self.model.nodes.count()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        query: Any = None,
        db_session: Any = None,
    ) -> list[ModelType]:
        if query is None:
            return await self.model.nodes.all()[skip:skip+limit]
        return await query[skip:skip+limit]

    async def get_multi_paginated(
        self,
        *,
        params: Params | None = Params(),
        query: Any = None,
        db_session: Any = None,
    ) -> Page[ModelType]:
        skip = (params.page - 1) * params.size
        limit = params.size
        nodes = await self.get_multi(skip=skip, limit=limit, query=query)
        return Page.create(items=nodes, total=await self.get_count(), params=params)

    async def get_multi_paginated_ordered(
        self,
        *,
        params: Params | None = Params(),
        order_by: str | None = None,
        order: IOrderEnum | None = IOrderEnum.ascendent,
        query: Any = None,
        db_session: Any = None,
    ) -> Page[ModelType]:
        skip = (params.page - 1) * params.size
        limit = params.size
        
        if order_by:
            order_str = "" if order == IOrderEnum.ascendent else "-"
            if query is None:
                query = self.model.nodes.order_by(f"{order_str}{order_by}")
            else:
                query = query.order_by(f"{order_str}{order_by}")
                
        return await self.get_multi_paginated(params=params, query=query)

    async def get_multi_ordered(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order: IOrderEnum | None = IOrderEnum.ascendent,
        db_session: Any = None,
    ) -> list[ModelType]:
        if order_by:
            order_str = "" if order == IOrderEnum.ascendent else "-"
            query = self.model.nodes.order_by(f"{order_str}{order_by}")
            return await query[skip:skip+limit]
        return await self.get_multi(skip=skip, limit=limit)

    async def create(
        self,
        *,
        obj_in: CreateSchemaType | ModelType,
        created_by_id: UUID | str | None = None,
        db_session: Any = None,
    ) -> ModelType:
        if isinstance(obj_in, self.model):
            db_obj = obj_in
        else:
            db_obj = self.model(**obj_in.dict())

        if created_by_id:
            db_obj.created_by_id = created_by_id

        try:
            await db_obj.save()
        except UniqueProperty:
            raise HTTPException(
                status_code=409,
                detail="Resource already exists",
            )
        return db_obj

    async def update(
        self,
        *,
        obj_current: ModelType,
        obj_new: UpdateSchemaType | dict[str, Any] | ModelType,
        db_session: Any = None,
    ) -> ModelType:
        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(obj_current, field, value)

        await obj_current.save()
        return obj_current

    async def remove(
        self, *, uid: UUID | str, db_session: Any = None
    ) -> ModelType:
        obj = await self.model.nodes.get(uid=uid)
        await obj.delete()
        return obj
