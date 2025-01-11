from fastapi.encoders import jsonable_encoder
from typing import TypeVar
from neomodel import StructuredNode

ModelType = TypeVar("ModelType", bound=StructuredNode)


def print_model(text: str = "", model: ModelType = []):
    """
    It prints neomodel responses for complex relationship models.
    """
    if isinstance(model, (list, tuple)):
        return print(text, [jsonable_encoder(m.__properties__) for m in model])
    return print(text, jsonable_encoder(model.__properties__))
