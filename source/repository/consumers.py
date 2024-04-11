from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from source.database.db import get_db
from source.models.models import Consumer
from source.schemas.consumer import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
        If no user is found, None is returned.
    
    :param email: str: Pass in the email address of the user to be retrieved
    :param db: AsyncSession: Pass in the database session
    :return: A user object or none
    :doc-author: Trelent
    """
    stmt = select(Consumer).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user

async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.
        It takes an email, username, and password as input.
        The function then hashes the password using bcrypt and stores it in the database.
    
    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Pass the database connection to the function
    :return: A consumer object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = Consumer(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def update_token(user: Consumer, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.
    
    :param user: Consumer: Identify the user that is being updated
    :param token: str | None: Update the refresh token of a user
    :param db: AsyncSession: Pass the database session to the function
    :return: A coroutine object
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()

async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function marks a user as confirmed in the database.
    
    :param email: str: Specify the email address of the user to be confirmed
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()
    return user

async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> Consumer:
    """
    The update_avatar_url function updates the avatar url of a user.
    
    :param email: str: Find the user in the database
    :param url: str | None: Determine if the avatar url is a string or none
    :param db: AsyncSession: Pass in the database session to be used for this function
    :return: The consumer object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(email: str, password:str, db: AsyncSession) -> None:
    """
    The update_password function updates the password of a user in the database.
    
    :param email: str: Specify the email of the user to update
    :param password:str: Update the password of a user
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.password = password
    await db.commit()
    return user