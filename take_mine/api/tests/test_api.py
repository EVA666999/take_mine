import pytest
from django.urls import reverse

from app.models import Category, Item


@pytest.mark.django_db
class TestSimpleAPI:
    """Базовые тесты для API"""

    def test_create_category(self, admin_auth_client):
        """Тест создания категории через API"""
        url = reverse("category-list")
        data = {"name": "API Category"}

        response = admin_auth_client.post(url, data, format="json")

        assert response.status_code == 201
        assert Category.objects.filter(name="API Category").exists()

    def test_create_item(self, admin_auth_client, category):
        """Тест создания предмета через API"""
        url = reverse("item-list")
        data = {
            "title": "API Item",
            "description": "API Description",
            "category": category.name,
            "condition": "new",
        }

        response = admin_auth_client.post(url, data, format="json")

        assert response.status_code == 201
        assert Item.objects.filter(title="API Item").exists()

    def test_edit_item(self, admin_auth_client, item):
        """Тест редактирования предмета через API"""
        url = reverse("item-detail", args=[item.id])
        data = {
            "title": "Updated API Item",
            "description": "Updated API Description",
            "category": item.category.name,
            "condition": "new",
        }

        response = admin_auth_client.put(url, data, format="json")

        assert response.status_code == 200

        # Проверяем, что данные обновились
        item.refresh_from_db()
        assert item.title == "Updated API Item"
        assert item.description == "Updated API Description"

    def test_delete_item(self, admin_auth_client, item):
        """Тест удаления предмета через API"""
        url = reverse("item-detail", args=[item.id])

        # Проверяем, что предмет существует
        assert Item.objects.filter(id=item.id).exists()

        # Удаляем предмет
        response = admin_auth_client.delete(url)

        assert response.status_code == 204

        # Проверяем, что предмет удален
        assert not Item.objects.filter(id=item.id).exists()

    def test_search_item(self, admin_auth_client, item, user, category):
        """Тест поиска предметов через API"""
        # Создаем дополнительный предмет для поиска
        Item.objects.create(
            user=user,
            title="Searchable Item",
            description="Searchable Description",
            category=category,
            condition="used",
        )

        # Поиск по заголовку
        url = reverse("item-list")
        response = admin_auth_client.get(url, {"search": "Searchable"})

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == "Searchable Item"
