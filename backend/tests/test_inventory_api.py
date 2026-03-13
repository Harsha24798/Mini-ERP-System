"""
Inventory API tests (Phase 3 starter)
"""

import json
from decimal import Decimal

from models import Category, Product, User, Warehouse, Stock


def _auth_headers(client, db_session, username="invuser", email="invuser@test.com"):
    user = User(
        username=username,
        email=email,
        first_name="Inv",
        last_name="User",
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "password123"},
    )
    tokens = json.loads(login_response.data)
    return {"Authorization": f"Bearer {tokens['access_token']}"}


class TestCategoryEndpoints:
    def test_list_categories_empty(self, client, db_session):
        response = client.get("/api/inventory/categories")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["categories"] == []

    def test_create_category_requires_auth(self, client, db_session):
        response = client.post(
            "/api/inventory/categories",
            json={"name": "Electronics"},
        )

        assert response.status_code == 401

    def test_create_and_get_category(self, client, db_session):
        headers = _auth_headers(client, db_session)

        create_response = client.post(
            "/api/inventory/categories",
            headers=headers,
            json={"name": "Electronics", "description": "Electronic items"},
        )

        assert create_response.status_code == 201
        create_data = json.loads(create_response.data)
        category_id = create_data["category"]["id"]

        get_response = client.get(f"/api/inventory/categories/{category_id}")
        assert get_response.status_code == 200
        get_data = json.loads(get_response.data)
        assert get_data["category"]["name"] == "Electronics"

    def test_update_and_delete_category(self, client, db_session):
        headers = _auth_headers(client, db_session, username="catuser", email="cat@test.com")

        category = Category(name="Hardware", description="Old")
        db_session.add(category)
        db_session.commit()

        update_response = client.put(
            f"/api/inventory/categories/{category.id}",
            headers=headers,
            json={"description": "Updated description"},
        )
        assert update_response.status_code == 200

        delete_response = client.delete(
            f"/api/inventory/categories/{category.id}",
            headers=headers,
        )
        assert delete_response.status_code == 200

        refreshed = Category.query.get(category.id)
        assert refreshed.is_active is False


class TestProductEndpoints:
    def test_create_product_and_filter_low_stock(self, client, db_session):
        headers = _auth_headers(client, db_session, username="produser", email="prod@test.com")

        category = Category(name="Components")
        warehouse = Warehouse(name="Main Warehouse", code="MAIN")
        db_session.add_all([category, warehouse])
        db_session.commit()

        create_response = client.post(
            "/api/inventory/products",
            headers=headers,
            json={
                "sku": "COMP-001",
                "name": "Capacitor",
                "category_id": category.id,
                "price": "12.50",
                "reorder_level": 10,
            },
        )

        assert create_response.status_code == 201
        product_id = json.loads(create_response.data)["product"]["id"]

        product = Product.query.get(product_id)
        stock = Stock(product_id=product.id, warehouse_id=warehouse.id, quantity=5)
        db_session.add(stock)
        db_session.commit()

        low_stock_response = client.get("/api/inventory/products/low-stock")
        assert low_stock_response.status_code == 200
        low_stock_data = json.loads(low_stock_response.data)
        assert low_stock_data["count"] == 1
        assert low_stock_data["products"][0]["sku"] == "COMP-001"

    def test_product_search(self, client, db_session):
        category = Category(name="Accessories")
        db_session.add(category)
        db_session.commit()

        db_session.add_all(
            [
                Product(
                    sku="CASE-001",
                    name="Phone Case",
                    category_id=category.id,
                    price=Decimal("19.99"),
                ),
                Product(
                    sku="CHRG-001",
                    name="Fast Charger",
                    category_id=category.id,
                    price=Decimal("29.99"),
                ),
            ]
        )
        db_session.commit()

        response = client.get("/api/inventory/products?search=case")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["products"]) == 1
        assert data["products"][0]["sku"] == "CASE-001"

    def test_update_product(self, client, db_session):
        headers = _auth_headers(client, db_session, username="updprod", email="updprod@test.com")

        category = Category(name="Peripherals")
        db_session.add(category)
        db_session.commit()

        product = Product(
            sku="MSE-001",
            name="Mouse",
            category_id=category.id,
            price=Decimal("15.00"),
        )
        db_session.add(product)
        db_session.commit()

        response = client.put(
            f"/api/inventory/products/{product.id}",
            headers=headers,
            json={"price": "17.50", "reorder_level": 3},
        )

        assert response.status_code == 200
        payload = json.loads(response.data)
        assert payload["product"]["price"] == 17.5
        assert payload["product"]["reorder_level"] == 3
