import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from app.models import Category, Item

User = get_user_model()

@pytest.fixture
def user(db):
    """Создаёт и возвращает тестового пользователя."""
    return User.objects.create_user(username='testuser', password='password')

@pytest.fixture
def admin_user(db):
    """Создаёт и возвращает тестового администратора."""
    return User.objects.create_user(username='admin', password='adminpass', is_staff=True)

@pytest.fixture
def user_auth_client(db, user):
    """Возвращает APIClient, аутентифицированный обычным пользователем."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def admin_auth_client(db, admin_user):
    """Возвращает APIClient, аутентифицированный админом."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client

@pytest.fixture
def category(db):
    """Создаёт и возвращает тестовую категорию."""
    return Category.objects.create(name='Test Category')

@pytest.fixture
def item(db, user, category):
    """Создаёт и возвращает тестовый предмет для обмена."""
    return Item.objects.create(
        user=user,
        title='Test Item',
        description='Test Description',
        category=category,
        condition='new'
    )
