from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.db import get_db
from source.repository import users as repository_users
from source.schemas.user import UserSchema, UserResponse

from source.models.models import Consumer, Role
from source.services.auth import auth_service
from source.services.roles import RoleAccess

from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix='/users', tags=['users'])

access_to_route_all = RoleAccess([Role.admin, Role.moderator]) 

@router.get("/", response_model=list[UserResponse])
async def get_users(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), c_user: Consumer = Depends(auth_service.get_current_user)):
    """
    The get_users function returns a list of users.
        The limit and offset parameters are used to paginate the results.
        The c_user parameter is used to determine if the user has access to this endpoint.
    
    :param limit: int: Limit the number of users returned
    :param ge: Set the minimum value of the limit parameter
    :param le: Limit the maximum number of users that can be returned
    :param offset: int: Skip the first n users
    :param ge: Set a minimum value for the limit parameter
    :param db: AsyncSession: Pass the database connection to the function
    :param c_user: Consumer: Get the current user from the database
    :return: A list of users, but the documentation says that it returns a user object
    :doc-author: Trelent
    """
    users = await repository_users.get_users(limit, offset, db, c_user)
    return users

@router.get("/all", response_model=list[UserResponse], dependencies=[Depends(access_to_route_all)])
async def get_all_users(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), c_user: Consumer = Depends(auth_service.get_current_user)):
    """
    The get_all_users function returns a list of all users in the database.
        The limit and offset parameters are used to paginate the results.
        
    
    :param limit: int: Limit the amount of users returned
    :param ge: Set the minimum value of the parameter
    :param le: Limit the maximum number of results returned
    :param offset: int: Skip a certain number of users
    :param ge: Specify the minimum value that can be passed to the limit parameter
    :param db: AsyncSession: Pass the database session to the function
    :param c_user: Consumer: Get the current user from the database
    :return: A list of users
    :doc-author: Trelent
    """
    users = await repository_users.get_all_users(limit, offset, db)
    return users

@router.get("/birth_date", response_model=list[UserResponse])
async def get_users_birth(limit: int = Query(7, ge=7, le=100),
                    db: AsyncSession = Depends(get_db), c_user: Consumer = Depends(auth_service.get_current_user)):
    """
    The get_users_birth function returns a list of users with their birthdays in the next 7 days.
        The limit parameter is optional and defaults to 7, but can be set to any number between 7 and 100.
    
    :param limit: int: Limit the amount of users returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the number of users returned
    :param db: AsyncSession: Pass the database session to the repository function
    :param c_user: Consumer: Get the current user from the auth_service
    :return: A list of users with the same birth date as the current user
    :doc-author: Trelent
    """
    users = await repository_users.get_users_birth(limit, db, c_user)
    return users

@router.get("/search_by", response_model=list[UserResponse])
async def get_users_by(first_name: str = Query(None, min_length=3, description="Frist name search query"), 
                       second_name: str = Query(None, min_length=3, description="Second name search query"),
                       email_add: str = Query(None, min_length=3, description="Email search query"),
                       db: AsyncSession = Depends(get_db), c_user: Consumer = Depends(auth_service.get_current_user)):
    """
    The get_users_by function is used to search for users by first name, second name or email address.
        The function will return a list of all the users that match the search criteria.
        If no user matches the search criteria an empty list will be returned.
    
    :param first_name: str: Pass the value of the first_name query parameter
    :param min_length: Specify the minimum length of the query string
    :param description: Create a description of the parameter in the swagger documentation
    :param second_name: str: Search for users by their second name
    :param min_length: Set a minimum length for the query string
    :param description: Provide a description for the parameter
    :param email_add: str: Search for users by email address
    :param min_length: Set the minimum length of the query string
    :param description: Provide a description of the parameter in the swagger documentation
    :param db: AsyncSession: Pass the database connection to the repository function
    :param c_user: Consumer: Get the current user
    :return: A list of users
    :doc-author: Trelent
    """
    users = await repository_users.get_users_by(first_name, second_name, email_add, db, c_user)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), c_user: Consumer = Depends(auth_service.get_current_user)):
    """
    The get_user function returns a user object based on the user_id passed in.
        If no such user exists, it will return an HTTP 404 error.
    
    :param user_id: int: Get the user_id from the path
    :param db: AsyncSession: Get a database connection from the dependency injection system
    :param c_user: Consumer: Get the current user from the auth_service
    :return: A user object
    :doc-author: Trelent
    """
    user = await repository_users.get_user(user_id, db, c_user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db), c_user: Consumer = Depends(auth_service.get_current_user)):
    """
    The create_user function creates a new user.
        The create_user function is used to create a new user in the database.
        ---
        tags:
          - users
        parameters:
          - name: body
            in: body # This means that the request will be sent as JSON data, not as form-data or query string parameters.  See https://swagger.io/docs/specification/describing-request-body/.  You can also use &quot;formData&quot; if you want to send it as form data instead of JSON (but I don't think this is
    
    :param body: UserSchema: Validate the request body against the userschema
    :param db: AsyncSession: Get the database session
    :param c_user: Consumer: Get the current user
    :return: A userschema object
    :doc-author: Trelent
    """
    user = await repository_users.create_user(body, db, c_user)
    return user


@router.put("/{user_id}")
async def update_user(body: UserSchema, user_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), c_user: Consumer = Depends(auth_service.get_current_user)):
    """
    The update_user function updates a user in the database.
        The function takes an id, body and db as parameters.
        It returns the updated user.
    
    :param body: UserSchema: Validate the body of the request
    :param user_id: int: Get the user_id from the url
    :param db: AsyncSession: Pass the database session to the repository function
    :param c_user: Consumer: Get the current user
    :return: The updated user
    :doc-author: Trelent
    """
    user = await repository_users.update_user(user_id, body, db, c_user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), c_user: Consumer = Depends(auth_service.get_current_user)):
    """
    The delete_user function deletes a user from the database.
        
    
    :param user_id: int: Get the user id from the url
    :param db: AsyncSession: Pass the database session to the repository
    :param c_user: Consumer: Get the current user from the auth_service
    :return: A user object
    :doc-author: Trelent
    """
    user = await repository_users.delete_user(user_id, db, c_user)
    return user
