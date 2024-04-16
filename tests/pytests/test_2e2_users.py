from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import pytest

from source.services.auth import auth_service


def test_get_users(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/users", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 0

def test_create_user(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("api/users", headers=headers, json={
            "first_name": "vlad",
            "second_name": "vladosovich",
            "email_add": "vlad@vladosovich.com",
            "phone_num": "11223124512",
            "birth_date": datetime.now().date() + timedelta(days=1),
        })
        assert response.status_code == 201, response.text
        print(response.text)
        data = response.json()
        assert "id" in data
        assert data["second_name"] == "vladosovich"
        assert data["email_add"] == "vlad@vladosovich.com"
        