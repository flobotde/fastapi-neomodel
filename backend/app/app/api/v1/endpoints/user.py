from io import BytesIO
from typing import Annotated
from uuid import UUID
from app.utils.exceptions import (
    IdNotFoundException,
    SelfFollowedException,
    UserFollowedException,
    UserNotFollowedException,
    UserSelfDeleteException,
)
from app import crud
from app.api import deps
from app.deps import user_deps
from app.models import User, UserFollow
from app.models.role_model import Role
from app.utils.minio_client import MinioClient
from app.utils.resize_image import modify_image
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Query,
    Response,
    UploadFile,
    status,
)
from app.schemas.media_schema import IMediaCreate
from app.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from app.schemas.role_schema import IRoleEnum
from app.schemas.user_follow_schema import IUserFollowRead
from app.schemas.user_schema import (
    IUserCreate,
    IUserRead,
    IUserReadWithoutGroups,
    IUserStatus,
)
from app.schemas.user_follow_schema import (
    IUserFollowReadCommon,
)
from fastapi_pagination import Params
from neomodel import db

router = APIRouter()


@router.get("/list")
async def read_users_list(
    params: Params = Depends(),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IGetResponsePaginated[IUserReadWithoutGroups]:
    """
    Retrieve users. Requires admin or manager role

    Required roles:
    - admin
    - manager
    """
    users = await User.nodes.filter(is_active=True).order_by('first_name').paginate(
        page=params.page,
        per_page=params.size
    )
    return create_response(data=users)


@router.get("/list/by_role_name")
async def read_users_list_by_role_name(
    name: str = "",
    user_status: Annotated[
        IUserStatus,
        Query(
            title="User status",
            description="User status (optional, default is active)",
        ),
    ] = IUserStatus.active,
    role_name: str = "",
    params: Params = Depends(),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IGetResponsePaginated[IUserReadWithoutGroups]:
    """
    Retrieve users by role name and status. Requires admin role

    Required roles:
    - admin
    """
    user_status = True if user_status == IUserStatus.active else False
    users = await User.nodes.filter(
        role__name__icontains=role_name,
        is_active=user_status,
        first_name__icontains=name
    ).order_by('first_name').paginate(
        page=params.page,
        per_page=params.size
    )
    return create_response(data=users)


@router.get("/order_by_created_at")
async def get_user_list_order_by_created_at(
    params: Params = Depends(),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IGetResponsePaginated[IUserReadWithoutGroups]:
    """
    Gets a paginated list of users ordered by created datetime

    Required roles:
    - admin
    - manager
    """
    users = await User.nodes.order_by('-created_at').paginate(
        page=params.page,
        per_page=params.size
    )
    return create_response(data=users)


@router.get("/following")
async def get_following(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IUserFollowReadCommon]:
    """
    Lists the people who the authenticated user follows.
    """
    users = await current_user.following.all()
    paginated_users = users.paginate(
        page=params.page,
        per_page=params.size
    )
    return create_response(data=users)


@router.get(
    "/following/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def check_is_followed_by_user_id(
    user: User = Depends(user_deps.is_valid_user),
    current_user: User = Depends(deps.get_current_user()),
):
    """
    Check if a person is followed by the authenticated user
    """
    result = await current_user.followers.is_connected(user)
    if not result:
        raise UserNotFollowedException(user_name=user.last_name)

    raise UserFollowedException(target_user_name=user.last_name)


@router.get("/followers")
async def get_followers(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IUserFollowReadCommon]:
    """
    Lists the people following the authenticated user.
    """
    users = await current_user.followers.all()
    paginated_users = users.paginate(
        page=params.page,
        per_page=params.size
    )
    return create_response(data=users)


@router.get("/{user_id}/followers")
async def get_user_followed_by_user_id(
    user_id: UUID = Depends(user_deps.is_valid_user_id),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IUserFollowReadCommon]:
    """
    Lists the people following the specified user.
    """
    user = await User.nodes.get(uid=user_id)
    users = await user.followers.all()
    paginated_users = users.paginate(
        page=params.page,
        per_page=params.size
    )
    return create_response(data=users)


@router.get("/{user_id}/following")
async def get_user_following_by_user_id(
    user_id: UUID = Depends(user_deps.is_valid_user_id),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IUserFollowReadCommon]:
    """
    Lists the people who the specified user follows.
    """
    user = await User.nodes.get(uid=user_id)
    users = await user.following.all()
    paginated_users = users.paginate(
        page=params.page,
        per_page=params.size
    )
    return create_response(data=users)


@router.get(
    "/{user_id}/following/{target_user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def check_a_user_is_followed_another_user_by_id(
    user_id: UUID,
    target_user_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
):
    """
    Check if a user follows another user
    """
    if user_id == target_user_id:
        raise SelfFollowedException()

    user = await User.nodes.get(uid=user_id)
    target_user = await User.nodes.get(uid=target_user_id)
    
    result = await user.following.is_connected(target_user)
    if not result:
        raise UserNotFollowedException(
            user_name=user.last_name, target_user_name=target_user.last_name
        )


@router.put("/following/{target_user_id}")
async def follow_a_user_by_id(
    target_user_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IPutResponseBase[IUserFollowRead]:
    """
    Following a user
    """
    if target_user_id == current_user.id:
        raise SelfFollowedException()
    target_user = await User.nodes.get(uid=target_user_id)
    
    if await current_user.following.is_connected(target_user):
        raise UserFollowedException(target_user_name=target_user.last_name)

    await current_user.following.connect(target_user)
    new_user_follow = await current_user.following.relationship(target_user)
    return create_response(data=new_user_follow)


@router.delete("/following/{target_user_id}")
async def unfollowing_a_user_by_id(
    target_user_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IDeleteResponseBase[IUserFollowRead]:
    """
    Unfollowing a user
    """
    if target_user_id == current_user.id:
        raise SelfFollowedException()
    target_user = await User.nodes.get(uid=target_user_id)
    
    if not await current_user.following.is_connected(target_user):
        raise UserNotFollowedException(user_name=target_user.last_name)

    await current_user.following.disconnect(target_user)
    user_follow = await current_user.following.relationship(target_user)
    return create_response(data=user_follow)


@router.get("/{user_id}")
async def get_user_by_id(
    user: User = Depends(user_deps.is_valid_user),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IGetResponseBase[IUserRead]:
    """
    Gets a user by his/her id

    Required roles:
    - admin
    - manager
    """
    return create_response(data=user)


@router.get("")
async def get_my_data(
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IUserRead]:
    """
    Gets my user profile information
    """
    return create_response(data=current_user)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    new_user: IUserCreate = Depends(user_deps.user_exists),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IPostResponseBase[IUserRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """
    user = await crud.user.create_with_role(obj_in=new_user)
    return create_response(data=user)


@router.delete("/{user_id}")
async def remove_user(
    user_id: UUID = Depends(user_deps.is_valid_user_id),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IDeleteResponseBase[IUserRead]:
    """
    Deletes a user by his/her id

    Required roles:
    - admin
    """
    if current_user.id == user_id:
        raise UserSelfDeleteException()

    user = await crud.user.remove(id=user_id)
    return create_response(data=user, message="User removed")


@router.post("/image")
async def upload_my_image(
    title: str | None = Body(None),
    description: str | None = Body(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user()),
    minio_client: MinioClient = Depends(deps.minio_auth),
) -> IPostResponseBase[IUserRead]:
    """
    Uploads a user image
    """
    try:
        image_modified = modify_image(BytesIO(image_file.file.read()))
        data_file = minio_client.put_object(
            file_name=image_file.filename,
            file_data=BytesIO(image_modified.file_data),
            content_type=image_file.content_type,
        )
        media = IMediaCreate(
            title=title, description=description, path=data_file.file_name
        )
        user = await crud.user.update_photo(
            user=current_user,
            image=media,
            heigth=image_modified.height,
            width=image_modified.width,
            file_format=image_modified.file_format,
        )
        return create_response(data=user)
    except Exception as e:
        print(e)
        return Response("Internal server error", status_code=500)


@router.post("/{user_id}/image")
async def upload_user_image(
    user: User = Depends(user_deps.is_valid_user),
    title: str | None = Body(None),
    description: str | None = Body(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
    minio_client: MinioClient = Depends(deps.minio_auth),
) -> IPostResponseBase[IUserRead]:
    """
    Uploads a user image by his/her id

    Required roles:
    - admin
    """
    try:
        image_modified = modify_image(BytesIO(image_file.file.read()))
        data_file = minio_client.put_object(
            file_name=image_file.filename,
            file_data=BytesIO(image_modified.file_data),
            content_type=image_file.content_type,
        )
        media = IMediaCreate(
            title=title, description=description, path=data_file.file_name
        )
        user = await crud.user.update_photo(
            user=user,
            image=media,
            heigth=image_modified.height,
            width=image_modified.width,
            file_format=image_modified.file_format,
        )
        return create_response(data=user)
    except Exception as e:
        print(e)
        return Response("Internal server error", status_code=500)
