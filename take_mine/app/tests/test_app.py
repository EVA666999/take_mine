# app/tests/test_app.py
import pytest
from django.contrib.auth import get_user_model

from app.models import Category, Item

User = get_user_model()


@pytest.mark.django_db
class TestSimpleApp:
    """Базовые тесты для приложения app"""

    def test_create_category(self):
        """Тест создания категории"""
        category = Category.objects.create(name="Test Category")
        assert category.name == "Test Category"
        assert Category.objects.count() == 1

    def test_create_item(self, user, category):
        """Тест создания предмета"""
        item = Item.objects.create(
            user=user,
            title="Test Item",
            description="Test Description",
            category=category,
            condition="new",
        )
        assert item.title == "Test Item"
        assert Item.objects.count() == 1

    def test_edit_item(self, user, category):
        """Тест редактирования предмета"""
        # Создаем предмет
        item = Item.objects.create(
            user=user,
            title="Original Title",
            description="Original Description",
            category=category,
            condition="new",
        )

        # Редактируем предмет
        item.title = "Updated Title"
        item.description = "Updated Description"
        item.condition = "used"
        item.save()

        # Проверяем, что данные обновились
        updated_item = Item.objects.get(id=item.id)
        assert updated_item.title == "Updated Title"
        assert updated_item.description == "Updated Description"
        assert updated_item.condition == "used"

    def test_delete_item(self, user, category):
        """Тест удаления предмета"""
        # Создаем предмет
        item = Item.objects.create(
            user=user,
            title="Item to Delete",
            description="Will be deleted",
            category=category,
            condition="new",
        )

        # Проверяем, что предмет создан
        assert Item.objects.count() == 1

        # Удаляем предмет
        item.delete()

        # Проверяем, что предмет удален
        assert Item.objects.count() == 0

    def test_search_item(self, user, category):
        """Тест поиска предметов"""
        # Создаем тестовые предметы
        Item.objects.create(
            user=user,
            title="First Item",
            description="First Description",
            category=category,
            condition="new",
        )

        Item.objects.create(
            user=user,
            title="Second Item",
            description="Second Description",
            category=category,
            condition="used",
        )

        # Поиск по заголовку
        results = Item.objects.filter(title__icontains="First")
        assert results.count() == 1
        assert results[0].title == "First Item"

        # Поиск по описанию
        results = Item.objects.filter(description__icontains="Second")
        assert results.count() == 1
        assert results[0].title == "Second Item"

        # Поиск по состоянию
        results = Item.objects.filter(condition="used")
        assert results.count() == 1
        assert results[0].title == "Second Item"
