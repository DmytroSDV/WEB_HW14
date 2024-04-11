import unittest
from unittest.mock import MagicMock, AsyncMock, Mock, patch

from sqlalchemy import TextClause, select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from source.models.models import Consumer, User
from source.schemas.user import UserSchema as U_schema
from source.schemas.consumer import UserSchema as C_schema
from source.repository.consumers import get_user_by_email, create_user, update_token, confirmed_email, update_avatar_url, update_password

class TestAsyncTodo(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.consumer = Consumer(id=1, username="Vlad", password="Vladislavovich", 
                                 email="Vlad@Vladislavovich.com", refresh_token='old_token',
                                 confirmed=False, avatar="old_url.com.ua", )
        self.session = AsyncMock(spec=AsyncSession)
        self.mocked_user = MagicMock()
        self.mocked_user.scalar_one_or_none.return_value = self.consumer
        self.session.execute.return_value = self.mocked_user

            
    async def test_get_user_by_email(self):
        email = "Vlad@Vladislavovich.com"

        result = await get_user_by_email(email, self.session)
        self.assertEqual(result, self.consumer)

    async def test_create_user(self):

        body = C_schema(username="Vlad", 
                email="Vlad@Vladislavovich.com",
                password="secretpsd")
        mocked_user = MagicMock()
        mocked_user.scalar.return_value.all.return_value = body
        self.session.execute.return_value = mocked_user

        new_user = await create_user(body, self.session)
        
        self.assertEqual(new_user.email, body.email)
        self.assertEqual(new_user.username, body.username)
        self.assertEqual(new_user.password, body.password)

        self.session.add.assert_called_once_with(new_user)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(new_user)

    async def test_update_token(self):
        new_token = 'new_token'

        await update_token(self.consumer, new_token, self.session)
        self.assertEqual(self.consumer.refresh_token, new_token)
        self.session.commit.assert_awaited_once()
    
    async def test_confirmed_email(self):

        upd_user = await confirmed_email(self.consumer.email, self.session)
        self.assertEqual(upd_user.confirmed, True)
        self.session.commit.assert_awaited_once()
    
    async def test_update_avatar_url(self):
        url = "new_url.com.ua"

        upd_user = await update_avatar_url(self.consumer.email, url, self.session)
        self.assertEqual(upd_user.avatar, url)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once()
    
    async def test_update_password(self):
        new_pass = "new_pass"

        upd_user = await update_password(self.consumer.email, new_pass, self.session)
        self.assertEqual(upd_user.password, new_pass)
        self.session.commit.assert_awaited_once()