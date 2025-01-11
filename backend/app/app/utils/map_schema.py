from typing import TypeVar
from pydantic import BaseModel
from neomodel import StructuredNode


SchemaType = TypeVar("SchemaType", bound=BaseModel)
ModelType = TypeVar("ModelType", bound=StructuredNode)


def map_models_schema(schema: SchemaType, models: list[ModelType]):
    """Map neomodel nodes to Pydantic schemas"""
    return [schema.parse_obj(model.__properties__) for model in models]
