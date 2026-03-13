"""
Inventory API tests (Phase 3)
"""

import json
from decimal import Decimal

from models import Category, Product, User, Warehouse, Stock, StockMovement


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


class TestWarehouseEndpoints:
    def test_create_list_update_delete_warehouse(self, client, db_session):
        headers = _auth_headers(client, db_session, username="whuser", email="whuser@test.com")

        create_response = client.post(
            "/api/inventory/warehouses",
            headers=headers,
            json={"name": "Central Warehouse", "code": "CENTRAL", "city": "Delhi"},
        )
        assert create_response.status_code == 201
        warehouse_id = json.loads(create_response.data)["warehouse"]["id"]

        list_response = client.get("/api/inventory/warehouses?search=central")
        assert list_response.status_code == 200
        list_data = json.loads(list_response.data)
        assert list_data["warehouses"][0]["code"] == "CENTRAL"

        update_response = client.put(
            f"/api/inventory/warehouses/{warehouse_id}",
            headers=headers,
            json={"city": "Noida", "phone": "9999999999"},
        )
        assert update_response.status_code == 200

        delete_response = client.delete(
            f"/api/inventory/warehouses/{warehouse_id}",
            headers=headers,
        )
        assert delete_response.status_code == 200

        refreshed = Warehouse.query.get(warehouse_id)
        assert refreshed.is_active is False


class TestStockMovementEndpoints:
    def test_record_in_and_out_movement_updates_stock(self, client, db_session):
        headers = _auth_headers(client, db_session, username="stkuser", email="stkuser@test.com")

        category = Category(name="Electrical")
        product = Product(
            sku="WIRE-001",
            name="Copper Wire",
            category=category,
            price=Decimal("100.00"),
            reorder_level=5,
        )
        warehouse = Warehouse(name="Store A", code="STA")
        db_session.add_all([category, product, warehouse])
        db_session.commit()

        in_response = client.post(
            "/api/inventory/stocks/movement",
            headers=headers,
            json={
                "product_id": product.id,
                "warehouse_id": warehouse.id,
                "movement_type": "IN",
                "quantity": 15,
                "notes": "Initial inward",
            },
        )
        assert in_response.status_code == 201
        in_data = json.loads(in_response.data)
        assert in_data["source_stock"]["quantity"] == 15

        out_response = client.post(
            "/api/inventory/stocks/movement",
            headers=headers,
            json={
                "product_id": product.id,
                "warehouse_id": warehouse.id,
                "movement_type": "OUT",
                "quantity": 4,
                "notes": "Order dispatch",
            },
        )
        assert out_response.status_code == 201
        out_data = json.loads(out_response.data)
        assert out_data["source_stock"]["quantity"] == 11

        stocks_response = client.get(
            f"/api/inventory/stocks?product_id={product.id}&warehouse_id={warehouse.id}"
        )
        assert stocks_response.status_code == 200
        stocks_data = json.loads(stocks_response.data)
        assert stocks_data["count"] == 1
        assert stocks_data["stocks"][0]["quantity"] == 11

    def test_transfer_movement_updates_both_warehouses(self, client, db_session):
        headers = _auth_headers(client, db_session, username="trfuser", email="trfuser@test.com")

        category = Category(name="Appliances")
        product = Product(
            sku="FAN-001",
            name="Table Fan",
            category=category,
            price=Decimal("1499.00"),
            reorder_level=3,
        )
        source_warehouse = Warehouse(name="North Depot", code="NDP")
        destination_warehouse = Warehouse(name="South Depot", code="SDP")
        db_session.add_all([category, product, source_warehouse, destination_warehouse])
        db_session.commit()

        seed_stock = Stock(
            product_id=product.id,
            warehouse_id=source_warehouse.id,
            quantity=20,
        )
        db_session.add(seed_stock)
        db_session.commit()

        transfer_response = client.post(
            "/api/inventory/stocks/movement",
            headers=headers,
            json={
                "product_id": product.id,
                "warehouse_id": source_warehouse.id,
                "to_warehouse_id": destination_warehouse.id,
                "movement_type": "TRANSFER",
                "quantity": 8,
                "notes": "Rebalancing stock",
            },
        )

        assert transfer_response.status_code == 201
        payload = json.loads(transfer_response.data)
        assert payload["movement_count"] == 2
        assert payload["source_stock"]["quantity"] == 12
        assert payload["destination_stock"]["quantity"] == 8

    def test_out_movement_fails_for_insufficient_stock(self, client, db_session):
        headers = _auth_headers(client, db_session, username="insuff", email="insuff@test.com")

        category = Category(name="Tools")
        product = Product(
            sku="HAM-001",
            name="Hammer",
            category=category,
            price=Decimal("250.00"),
        )
        warehouse = Warehouse(name="Tool Hub", code="THB")
        db_session.add_all([category, product, warehouse])
        db_session.commit()

        db_session.add(
            Stock(product_id=product.id, warehouse_id=warehouse.id, quantity=2)
        )
        db_session.commit()

        response = client.post(
            "/api/inventory/stocks/movement",
            headers=headers,
            json={
                "product_id": product.id,
                "warehouse_id": warehouse.id,
                "movement_type": "OUT",
                "quantity": 3,
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Insufficient stock" in data["error"]

    def test_list_stock_movements(self, client, db_session):
        headers = _auth_headers(client, db_session, username="mvuser", email="mvuser@test.com")

        category = Category(name="Consumables")
        product = Product(
            sku="INK-001",
            name="Printer Ink",
            category=category,
            price=Decimal("799.00"),
        )
        warehouse = Warehouse(name="Print Store", code="PST")
        db_session.add_all([category, product, warehouse])
        db_session.commit()

        movement = StockMovement(
            product_id=product.id,
            warehouse_id=warehouse.id,
            movement_type="IN",
            quantity=5,
            notes="Manual seed",
        )
        db_session.add(movement)
        db_session.commit()

        response = client.get(
            f"/api/inventory/stocks/movements?product_id={product.id}&movement_type=in"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["count"] == 1
        assert data["movements"][0]["movement_type"] == "IN"

        create_response = client.post(
            "/api/inventory/stocks/movement",
            headers=headers,
            json={
                "product_id": product.id,
                "warehouse_id": warehouse.id,
                "movement_type": "ADJUSTMENT",
                "quantity": 2,
            },
        )
        assert create_response.status_code == 201
