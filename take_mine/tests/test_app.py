import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from app.models import Category, Item, ExchangeProposal

User = get_user_model()

@pytest.fixture(scope='session')
def django_db_setup():
    """
    Настройка тестовой базы данных для pytest.
    Использует SQLite для тестов вместо PostgreSQL.
    """
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

@pytest.fixture
def api_client():
    """Фикстура для создания API-клиента"""
    return APIClient()

@pytest.fixture
def user():
    """Фикстура для создания тестового пользователя"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword'
    )

@pytest.fixture
def admin_user():
    """Фикстура для создания тестового администратора"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword'
    )

@pytest.fixture
def another_user():
    """Фикстура для создания второго тестового пользователя"""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='anotherpassword'
    )

@pytest.fixture
def auth_client(api_client, user):
    """Фикстура для создания авторизованного API-клиента"""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.fixture
def auth_admin_client(api_client, admin_user):
    """Фикстура для создания авторизованного API-клиента администратора"""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.fixture
def another_auth_client(api_client, another_user):
    """Фикстура для создания второго авторизованного API-клиента"""
    refresh = RefreshToken.for_user(another_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.fixture
def category():
    """Фикстура для создания тестовой категории"""
    return Category.objects.create(
        name='Test Category',
        slug='test-category'
    )

@pytest.fixture
def item(user, category):
    """Фикстура для создания тестового предмета"""
    return Item.objects.create(
        user=user,
        title='Test Item',
        description='Test Description',
        category=category,
        condition='used'
    )

@pytest.fixture
def another_item(another_user, category):
    """Фикстура для создания второго тестового предмета"""
    return Item.objects.create(
        user=another_user,
        title='Another Item',
        description='Another Description',
        category=category,
        condition='new'
    )

@pytest.fixture
def exchange_proposal(item, another_item):
    """Фикстура для создания тестового предложения обмена"""
    return ExchangeProposal.objects.create(
        ad_sender=item,
        ad_receiver=another_item,
        comment='Test Exchange Proposal',
        status='ожидает'
    )