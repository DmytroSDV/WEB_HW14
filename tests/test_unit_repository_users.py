import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from source.models.models import Consumer, User
from source.schemas.user import UserSchema, UserResponse
from source.repository.users import get_users, get_all_users, get_users_by, get_user, get_users_birth, create_user, update_user, delete_user

from datetime import datetime, timedelta

class TestAsyncTodo(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.consumer = Consumer(id=1, username='test_user', password="qwerty", confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_all_users(self):
        limit = 10
        offset = 0
        users = [User(id=1, first_name='Valentin', second_name='Valentinovich', email_add="valia@valik.com", 
                      phone_num="55556", birth_date="01-02-2001", consumer=self.consumer),
                User(id=1, first_name='Stepan', second_name='Stepanovich', email_add="stepa@stepik.com", 
                      phone_num="52356", birth_date="04-12-2004", consumer=self.consumer)]
        mocked_users = MagicMock()
        mocked_users.scalars.return_value.all.return_value = users
        self.session.execute.return_value = mocked_users
        result = await get_all_users(limit, offset, self.session)
        self.assertEqual(result, users)

    async def test_get_users(self):
        limit = 10
        offset = 0
        users = [User(id=1, first_name='Valentin', second_name='Valentinovich', email_add="valia@valik.com", 
                      phone_num="55556", birth_date="01-02-2001", consumer=self.consumer),
                User(id=1, first_name='Stepan', second_name='Stepanovich', email_add="stepa@stepik.com", 
                      phone_num="52356", birth_date="04-12-2004", consumer=self.consumer)]
        mocked_users = MagicMock()
        mocked_users.scalars.return_value.all.return_value = users
        self.session.execute.return_value = mocked_users
        result = await get_users(limit, offset, self.session, self.consumer)
        self.assertEqual(result, users)

    async def test_create_user(self):
        body = UserSchema(first_name="Valentin", second_name="Valentinovich", 
                          email_add="valia@valik.com",
                          phone_num="55556", birth_date=datetime.now().date()-timedelta(days=342))
        result = await create_user(body, self.session, self.consumer)
        self.assertIsInstance(result, User)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.email_add, body.email_add)