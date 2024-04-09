import pickle

import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Path,
    Query,
    UploadFile,
    File,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.db import get_db
from source.models.models import Consumer
from source.schemas.consumer import UserResponse
from source.services.auth import auth_service
from source.config.conf import config
from source.repository import consumers as repository_consumer


router = APIRouter(prefix="/users-profile", tags=["users-profile"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=10))],
)
async def get_current_user(user: Consumer = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It will return the current user, if any.
    
    :param user: Consumer: Get the current user
    :return: The user object
    :doc-author: Trelent
    """
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=10))],
)
async def get_current_user(
    file: UploadFile = File(),
    user: Consumer = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The get_current_user function is used to update the avatar url of a user.
        The function takes in an UploadFile object, which contains the file that will be uploaded to Cloudinary.
        It also takes in a Consumer object, which represents the current logged-in user and is obtained from auth_service's get_current_user function.
        Finally it takes in an AsyncSession object, which represents our database session and is obtained from get_db().
    
    :param file: UploadFile: Get the file that is being uploaded
    :param user: Consumer: Get the current user from the database
    :param db: AsyncSession: Get the database session
    :param : Get the current user from the database
    :return: The following error:
    :doc-author: Trelent
    """
    public_id = f"Web16/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repository_consumer.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user

