from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from source.models.models import User, Consumer
from source.schemas.user import UserSchema

from datetime import datetime, timedelta

async def get_users(limit: int, offset: int, db: AsyncSession, consumer: Consumer):
    """
    The get_users function returns a list of users from the database.
    
    :param limit: int: Limit the number of users returned
    :param offset: int: Specify the number of records to skip
    :param db: AsyncSession: Pass the database session to the function
    :param consumer: Consumer: Filter the users by consumer
    :return: A list of user objects
    :doc-author: Trelent
    """
    search = select(User).filter_by(consumer=consumer).offset(offset).limit(limit)
    users = await db.execute(search)
    return users.scalars().all()

async def get_all_users(limit: int, offset: int, db: AsyncSession):
    """
    The get_all_users function returns a list of all users in the database.
    
    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the number of rows to skip
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of user objects
    :doc-author: Trelent
    """
    search = select(User).offset(offset).limit(limit)
    users = await db.execute(search)
    return users.scalars().all()

async def get_users_by(first_name: str = None, 
                       second_name: str = None, 
                       email_add: str = None, db: AsyncSession = None, 
                       consumer: Consumer = None):
    
    """
    The get_users_by function is used to search for users in the database.
    It takes a first_name, second_name and email address as arguments. 
    If any of these are provided, it will return all users that match the criteria.
    
    :param first_name: str: Search for a user with the first name
    :param second_name: str: Filter the users by their second name
    :param email_add: str: Search for a user by email address
    :param db: AsyncSession: Pass in the database session to be used for querying
    :param consumer: Consumer: Filter the users by consumer
    :return: A list of user objects
    :doc-author: Trelent
    """
    search = select(User).filter_by(consumer=consumer)
    if first_name and second_name and email_add:
        search = search.where(or_(User.first_name == first_name, User.second_name == second_name, User.email_add == email_add))

    elif first_name and second_name:
        search = search.where(or_(User.first_name == first_name, User.second_name == second_name, User.email_add == email_add))

    elif first_name and email_add:
        search = search.where(or_(User.first_name == first_name, User.email_add == email_add))
    
    elif second_name and email_add:
        search = search.where(or_(User.second_name == second_name, User.email_add == email_add))
    
    elif first_name:
        search = search.where(User.first_name == first_name)
        
    elif second_name:
        search = search.where(User.second_name == second_name)
        
    elif email_add:
        search = search.where(User.email_add == email_add)
    
    else:
        return []

    users = await db.execute(search)
    print(type(users.scalars().all()))
    return users.scalars().all()

async def get_user(user_id: int, db: AsyncSession, consumer: Consumer):
    """
    The get_user function is used to retrieve a user from the database.
    
    :param user_id: int: Specify the user id of the user that we want to retrieve
    :param db: AsyncSession: Pass in the database session
    :param consumer: Consumer: Filter the user by consumer
    :return: An object of the user class
    :doc-author: Trelent
    """
    search = select(User).filter_by(id=user_id, consumer=consumer)
    user = await db.execute(search)
    return user.scalar_one_or_none()

async def get_users_birth(limit: int, db: AsyncSession, consumer: Consumer):
    
    """
    The get_users_birth function returns a list of users whose birthdays are within the next `limit` days.
    
    :param limit: int: Limit the number of days to search for birthdays
    :param db: AsyncSession: Pass the database session to the function
    :param consumer: Consumer: Filter the search by consumer
    :return: A list of users with a birth date in the next limit days
    :doc-author: Trelent
    """
    current_date = datetime.now().date()
    end_date = current_date + timedelta(days=limit)
    
    search = (
        select(User)
        .filter(User.birth_date >= current_date)
        .filter(User.birth_date <= end_date)
        .filter(User.consumer == consumer)
    )
    result = await db.execute(search)

    return result.scalars().all()

async def create_user(body: UserSchema, db: AsyncSession, consumer: Consumer):
    """
    The create_user function creates a new user.
    
    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param consumer: Consumer: Create the user
    :return: A user object
    :doc-author: Trelent
    """
    user = User(**body.model_dump(exclude_unset=True), consumer=consumer)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(user_id: int, body: UserSchema, db: AsyncSession, consumer: Consumer):
    """
    The update_user function updates a user in the database.
        Args:
            user_id (int): The id of the user to update.
            body (UserSchema): A UserSchema object containing all fields that should be updated for this user. 
                Note that only fields included in this schema will be updated, and any other fields will remain unchanged.
            db (AsyncSession): An async session with an open transaction to use for querying and updating data from the database.
            consumer(Consumer): The consumer associated with this request, used as a filter when querying users from the
    
    :param user_id: int: Identify the user in the database
    :param body: UserSchema: Pass the user data that will be used to update a user
    :param db: AsyncSession: Pass the database session to the function
    :param consumer: Consumer: Ensure that the user is only updated if they are a consumer of the company
    :return: A user object
    :doc-author: Trelent
    """
    search = select(User).filter_by(id=user_id, consumer=consumer)
    result = await db.execute(search)
    user = result.scalar_one_or_none()
    if user:
        user.first_name = body.first_name
        user.second_name = body.second_name
        user.email_add = body.email_add
        user.phone_num = body.phone_num
        user.birth_date = body.birth_date
        await db.commit()
        await db.refresh(user)
    return  user

async def delete_user(user_id: int, db: AsyncSession, consumer: Consumer):
    """
    The delete_user function deletes a user from the database.
    
    :param user_id: int: Specify the user that will be deleted
    :param db: AsyncSession: Create a connection to the database
    :param consumer: Consumer: Filter the user by consumer
    :return: A user object if the user was deleted, otherwise it returns none
    :doc-author: Trelent
    """
    search = select(User).filter_by(id=user_id, consumer=consumer)
    user = await db.execute(search)
    user = user.scalar_one_or_none()
    if user:
        await db.delete(user)
        await db.commit()
    return user
