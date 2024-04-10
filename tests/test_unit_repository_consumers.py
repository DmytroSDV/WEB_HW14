import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy import TextClause, select
from sqlalchemy.ext.asyncio import AsyncSession

from source.models.models import Consumer, User
from source.schemas.user import UserSchema, UserResponse
from source.repository.consumers import get_user_by_email, create_user, update_token, confirmed_email, update_avatar_url, update_password

class TestAsyncTodo(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
            
    async def test_get_user_by_email(self):
        email = "valentinka@kolobok.com"
        user = Consumer(id=1, username="Vlad", password="Vladislavovich", email="Vlad@Vladislavovich.com")
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(email, self.session)

        self.assertEqual(result, user)
