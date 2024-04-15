from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from datetime import datetime, timedelta

from source.models.models import User
from source.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = AsyncMock()
    monkeypatch.setattr("source.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_create_user(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/users",
            json={"first_name": "Vlad", "second_name":"Vladislavovich", 
                  "email_add":"vladislavna@gmail.com", "phone_num": "123",
                  "birth_date": datetime.now().date() - timedelta(days=1245)},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["second_name"] == "Vladislavovich"
        assert "id" in data


def test_get_user(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/users/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["second_name"] == "Vladislavovich"
        assert "id" in data


def test_get_user_not_found(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/users/2",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "NOT FOUND"


def test_get_users(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["first_name"] == "Vlad"
        assert "id" in data[0]


def test_update_user(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/api/users/1",
            json={"first_name": "Vladik", "second_name":"Vladislavovich", 
                  "email_add":"vladislavna@gmail.com", "phone_num": "12455",
                  "birth_date": datetime.now().date() - timedelta(days=124)},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == "Vladik"
        assert "id" in data


def test_update_user_not_found(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/api/users/2",
            json={"first_name": "Vladik", "second_name":"Vladislavovich", 
                  "email_add":"vladislavna@gmail.com", "phone_num": "12455",
                  "birth_date": datetime.now().date() - timedelta(days=124)},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "NOT FOUND"


def test_delete_user(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/users/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == "Vladik"
        assert "id" in data


def test_repeat_delete_user(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/users/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "NOT FOUND"
