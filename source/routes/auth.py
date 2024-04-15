from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.db import get_db
from source.repository import consumers as repository_consumer
from source.schemas.consumer import UserSchema, TokenSchema, UserResponse, RequestEmail, PasswordForm
from source.services.auth import auth_service
from source.services.email import send_email, send_password_email

from fastapi_limiter.depends import RateLimiter
from source.config import messages
router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()



@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    The signup function creates a new user in the database.
    
    :param body: UserSchema: Get the request body from the user
    :param bt: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base_url of the request
    :param db: AsyncSession: Get the database session
    :return: A userschema object
    :doc-author: Trelent
    """
    exist_user = await repository_consumer.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_consumer.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    # return {
    #     "user": new_user,
    #     "detail": "User successfully created. Check your email for confirmation.",
    # }
    return new_user
    
@router.post("/login",  response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    
    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: AsyncSession: Get the database session
    :return: A dictionary with the access token and refresh token
    :doc-author: Trelent
    """
    user = await repository_consumer.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "Tester Testorovich"})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_consumer.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    
@router.get('/refresh_token',  response_model=TokenSchema, dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function will take in a refresh token and return an access_token, 
        a new refresh_token, and the type of token (bearer).
    
    :param credentials: HTTPAuthorizationCredentials: Get the refresh token from the request header
    :param db: AsyncSession: Create a database session
    :return: A dictionary with the following keys:
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_consumer.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_consumer.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_consumer.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    
@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it checks if that user exists in our database, and if they do not exist, 
        we return an error message saying &quot;Verification error&quot;. If they do exist in our database, 
        we check whether or not their account has already been confirmed. If their account has already been confirmed, 
        then we return a message saying &quot;Your email is already confirmed&quot;. Otherwise (if their account hasn't yet been confirmed), 
    
    :param token: str: Get the token from the url
    :param db: AsyncSession: Get the database connection
    :return: A dictionary with a message key and value
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_consumer.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_consumer.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email', dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to confirm their email address. The function takes in a RequestEmail object, which contains the 
    email of the user who wants to confirm their account. It then checks if there is already a confirmed 
    user with that email address, and if so returns an error message saying as much. If not, it sends an 
    email containing a confirmation link.
    
    :param body: RequestEmail: Validate the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: AsyncSession: Get the database session
    :return: A dict, but the return type is a response
    :doc-author: Trelent
    """
    user = await repository_consumer.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}

@router.get('/new-password/{token}')
async def new_password(token: str, db: AsyncSession = Depends(get_db)):
    """
    The new_password function is used to update a user's password.
        It takes in the token and db as parameters, and returns a message indicating that the password has been updated.
    
    
    :param token: str: Get the token from the request body
    :param db: AsyncSession: Pass the database connection to the function
    :return: A dict with a message
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    password = await auth_service.get_password_from_token(token)
    user = await repository_consumer.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if password:
        password = auth_service.get_password_hash(password)
        await repository_consumer.update_password(email, password, db)
    return {"message": "New password succesfully updated!"}

@router.post('/reset-password', dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def reset_password(body: PasswordForm, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    The reset_password function is used to reset a user's password.
        It takes in the email of the user, and then sends an email with a link to reset their password.
        The link will expire after 1 hour.
    
    :param body: PasswordForm: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: AsyncSession: Create a database session
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    user = await repository_consumer.get_user_by_email(body.email, db)
    if user:
        if body.password == body.password_confirm:
            background_tasks.add_task(send_password_email, user.email, user.username, body.password, str(request.base_url))
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Passwords do not match!")
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Such email does not exist!")
    
    return {"message": "Check your email, link for password reset was sended."}