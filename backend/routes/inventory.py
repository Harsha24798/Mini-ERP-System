"""
Inventory Routes
Phase 3 starter endpoints for category and product management.
"""

from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from extensions import db
from models import Category, Product, Warehouse, Stock, StockMovement
from utils.auth import token_required, get_current_user


inventory_bp = Blueprint("inventory", __name__)


def _parse_bool(value):
    if value is None:
        return None
    return str(value).lower() in {"1", "true", "yes", "on"}


def _parse_positive_int(value, field_name):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid integer")

    if parsed < 0:
        raise ValueError(f"{field_name} must be greater than or equal to 0")

    return parsed


def _parse_int(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid integer")


def _parse_decimal(value, field_name):
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid decimal value")

    if parsed < 0:
        raise ValueError(f"{field_name} must be greater than or equal to 0")

    return parsed


def _get_or_create_stock(product_id, warehouse_id):
    stock = Stock.query.filter_by(product_id=product_id, warehouse_id=warehouse_id).first()
    if stock:
        return stock

    stock = Stock(product_id=product_id, warehouse_id=warehouse_id, quantity=0)
    db.session.add(stock)
    db.session.flush()
    return stock


@inventory_bp.route("/categories", methods=["GET"])
def list_categories():
    """List categories with optional filtering."""
    search = request.args.get("search", type=str)
    is_active = _parse_bool(request.args.get("is_active"))

    query = Category.query

    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))

    if is_active is not None:
        query = query.filter(Category.is_active == is_active)

    categories = query.order_by(Category.name.asc()).all()

    return jsonify({"categories": [category.to_dict() for category in categories]}), 200


@inventory_bp.route("/categories", methods=["POST"])
@token_required
def create_category():
    """Create a new category."""
    try:
        data = request.get_json() or {}

        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "name is required"}), 400

        existing = Category.query.filter(Category.name.ilike(name)).first()
        if existing:
            return jsonify({"error": "Category with this name already exists"}), 400

        parent_id = data.get("parent_id")
        if parent_id is not None:
            try:
                parent_id = int(parent_id)
            except (TypeError, ValueError):
                return jsonify({"error": "parent_id must be a valid integer"}), 400

            if not Category.query.get(parent_id):
                return jsonify({"error": "Parent category not found"}), 404

        category = Category(
            name=name,
            description=data.get("description"),
            parent_id=parent_id,
            is_active=data.get("is_active", True),
        )

        db.session.add(category)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Category created successfully",
                    "category": category.to_dict(),
                }
            ),
            201,
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Failed to create category", "details": str(exc)}), 500


@inventory_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    """Get category details by id."""
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify({"category": category.to_dict()}), 200


@inventory_bp.route("/categories/<int:category_id>", methods=["PUT"])
@token_required
def update_category(category_id):
    """Update category details."""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404

        data = request.get_json() or {}

        if "name" in data:
            name = (data.get("name") or "").strip()
            if not name:
                return jsonify({"error": "name cannot be empty"}), 400

            duplicate = Category.query.filter(
                Category.id != category.id,
                Category.name.ilike(name),
            ).first()
            if duplicate:
                return jsonify({"error": "Category with this name already exists"}), 400
            category.name = name

        if "description" in data:
            category.description = data.get("description")

        if "is_active" in data:
            category.is_active = bool(data.get("is_active"))

        if "parent_id" in data:
            parent_id = data.get("parent_id")
            if parent_id is None:
                category.parent_id = None
            else:
                try:
                    parent_id = int(parent_id)
                except (TypeError, ValueError):
                    return jsonify({"error": "parent_id must be a valid integer"}), 400

                if parent_id == category.id:
                    return jsonify({"error": "Category cannot be its own parent"}), 400

                parent = Category.query.get(parent_id)
                if not parent:
                    return jsonify({"error": "Parent category not found"}), 404

                category.parent_id = parent_id

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Category updated successfully",
                    "category": category.to_dict(),
                }
            ),
            200,
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Failed to update category", "details": str(exc)}), 500


@inventory_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@token_required
def delete_category(category_id):
    """Soft-delete category by setting is_active=False."""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404

        category.is_active = False
        db.session.commit()

        return jsonify({"message": "Category deactivated successfully"}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Failed to delete category", "details": str(exc)}), 500


@inventory_bp.route("/products", methods=["GET"])
def list_products():
    """List products with optional search and low-stock filtering."""
    search = request.args.get("search", type=str)
    category_id = request.args.get("category_id")
    low_stock = _parse_bool(request.args.get("low_stock"))
    is_active = _parse_bool(request.args.get("is_active"))

    query = Product.query

    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%"),
            )
        )

    if category_id is not None:
        try:
            category_id = int(category_id)
        except (TypeError, ValueError):
            return jsonify({"error": "category_id must be a valid integer"}), 400
        query = query.filter(Product.category_id == category_id)

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    products = query.order_by(Product.name.asc()).all()

    if low_stock is True:
        products = [product for product in products if product.is_low_stock]

    return jsonify({"products": [product.to_dict() for product in products]}), 200


@inventory_bp.route("/products", methods=["POST"])
@token_required
def create_product():
    """Create a new product."""
    try:
        data = request.get_json() or {}

        required_fields = ["sku", "name", "category_id", "price"]
        for field in required_fields:
            if data.get(field) in (None, ""):
                return jsonify({"error": f"{field} is required"}), 400

        sku = str(data["sku"]).strip()
        name = str(data["name"]).strip()
        if not sku or not name:
            return jsonify({"error": "sku and name are required"}), 400

        if Product.query.filter_by(sku=sku).first():
            return jsonify({"error": "Product SKU already exists"}), 400

        barcode = data.get("barcode")
        if barcode and Product.query.filter_by(barcode=barcode).first():
            return jsonify({"error": "Product barcode already exists"}), 400

        category_id = _parse_positive_int(data.get("category_id"), "category_id")
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404

        price = _parse_decimal(data.get("price"), "price")
        cost = data.get("cost")
        if cost is not None:
            cost = _parse_decimal(cost, "cost")

        reorder_level = data.get("reorder_level", 10)
        reorder_level = _parse_positive_int(reorder_level, "reorder_level")

        product = Product(
            sku=sku,
            name=name,
            description=data.get("description"),
            category_id=category_id,
            unit=data.get("unit", "pcs"),
            price=price,
            cost=cost,
            reorder_level=reorder_level,
            image_url=data.get("image_url"),
            barcode=barcode,
            is_active=data.get("is_active", True),
        )

        db.session.add(product)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Product created successfully",
                    "product": product.to_dict(),
                }
            ),
            201,
        )
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Failed to create product", "details": str(exc)}), 500


@inventory_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Get product details by id."""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"product": product.to_dict()}), 200


@inventory_bp.route("/products/<int:product_id>", methods=["PUT"])
@token_required
def update_product(product_id):
    """Update product details."""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        data = request.get_json() or {}

        if "sku" in data:
            sku = str(data.get("sku") or "").strip()
            if not sku:
                return jsonify({"error": "sku cannot be empty"}), 400

            duplicate = Product.query.filter(
                Product.id != product.id,
                Product.sku == sku,
            ).first()
            if duplicate:
                return jsonify({"error": "Product SKU already exists"}), 400
            product.sku = sku

        if "name" in data:
            name = str(data.get("name") or "").strip()
            if not name:
                return jsonify({"error": "name cannot be empty"}), 400
            product.name = name

        if "description" in data:
            product.description = data.get("description")

        if "category_id" in data:
            category_id = _parse_positive_int(data.get("category_id"), "category_id")
            category = Category.query.get(category_id)
            if not category:
                return jsonify({"error": "Category not found"}), 404
            product.category_id = category_id

        if "price" in data:
            product.price = _parse_decimal(data.get("price"), "price")

        if "cost" in data:
            cost = data.get("cost")
            product.cost = None if cost is None else _parse_decimal(cost, "cost")

        if "reorder_level" in data:
            product.reorder_level = _parse_positive_int(
                data.get("reorder_level"), "reorder_level"
            )

        if "unit" in data:
            product.unit = data.get("unit") or "pcs"

        if "image_url" in data:
            product.image_url = data.get("image_url")

        if "barcode" in data:
            barcode = data.get("barcode")
            if barcode:
                duplicate_barcode = Product.query.filter(
                    Product.id != product.id,
                    Product.barcode == barcode,
                ).first()
                if duplicate_barcode:
                    return jsonify({"error": "Product barcode already exists"}), 400
            product.barcode = barcode

        if "is_active" in data:
            product.is_active = bool(data.get("is_active"))

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Product updated successfully",
                    "product": product.to_dict(),
                }
            ),
            200,
        )
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Failed to update product", "details": str(exc)}), 500


@inventory_bp.route("/products/<int:product_id>", methods=["DELETE"])
@token_required
def delete_product(product_id):
    """Soft-delete product by setting is_active=False."""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        product.is_active = False
        db.session.commit()

        return jsonify({"message": "Product deactivated successfully"}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Failed to delete product", "details": str(exc)}), 500


@inventory_bp.route("/products/low-stock", methods=["GET"])
def low_stock_products():
    """Get products currently at or below reorder level."""
    products = Product.query.filter_by(is_active=True).all()
    low_stock_items = [product.to_dict() for product in products if product.is_low_stock]

    return jsonify({"products": low_stock_items, "count": len(low_stock_items)}), 200


@inventory_bp.route("/warehouses", methods=["GET"])
def list_warehouses():
    """List warehouses with optional filtering."""
    search = request.args.get("search", type=str)
    is_active = _parse_bool(request.args.get("is_active"))

    query = Warehouse.query

    if search:
        query = query.filter(
            db.or_(
                Warehouse.name.ilike(f"%{search}%"),
                Warehouse.code.ilike(f"%{search}%"),
            )
        )

    if is_active is not None:
        query = query.filter(Warehouse.is_active == is_active)

    warehouses = query.order_by(Warehouse.name.asc()).all()
    return jsonify({"warehouses": [warehouse.to_dict() for warehouse in warehouses]}), 200


@inventory_bp.route("/warehouses", methods=["POST"])
@token_required
def create_warehouse():
    """Create a new warehouse."""
    try:
        data = request.get_json() or {}

        name = (data.get("name") or "").strip()
        code = (data.get("code") or "").strip()

        if not name:
            return jsonify({"error": "name is required"}), 400
        if not code:
            return jsonify({"error": "code is required"}), 400

        existing_name = Warehouse.query.filter(Warehouse.name.ilike(name)).first()
        if existing_name:
            return jsonify({"error": "Warehouse with this name already exists"}), 400

        existing_code = Warehouse.query.filter(Warehouse.code.ilike(code)).first()
        if existing_code:
            return jsonify({"error": "Warehouse with this code already exists"}), 400

        warehouse = Warehouse(
            name=name,
            code=code,
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            country=data.get("country"),
            postal_code=data.get("postal_code"),
            phone=data.get("phone"),
            is_active=data.get("is_active", True),
        )

        db.session.add(warehouse)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Warehouse created successfully",
                    "warehouse": warehouse.to_dict(),
                }
            ),
            201,
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Failed to create warehouse", "details": str(exc)}), 500


@inventory_bp.route("/warehouses/<int:warehouse_id>", methods=["GET"])
def get_warehouse(warehouse_id):
    """Get warehouse details by id."""
    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return jsonify({"error": "Warehouse not found"}), 404

    return jsonify({"warehouse": warehouse.to_dict()}), 200


@inventory_bp.route("/warehouses/<int:warehouse_id>", methods=["PUT"])
@token_required
def update_warehouse(warehouse_id):
    """Update warehouse details."""
    try:
        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        data = request.get_json() or {}

        if "name" in data:
            name = (data.get("name") or "").strip()
            if not name:
                return jsonify({"error": "name cannot be empty"}), 400

            duplicate_name = Warehouse.query.filter(
                Warehouse.id != warehouse.id,
                Warehouse.name.ilike(name),
            ).first()
            if duplicate_name:
                return jsonify({"error": "Warehouse with this name already exists"}), 400
            warehouse.name = name

        if "code" in data:
            code = (data.get("code") or "").strip()
            if not code:
                return jsonify({"error": "code cannot be empty"}), 400

            duplicate_code = Warehouse.query.filter(
                Warehouse.id != warehouse.id,
                Warehouse.code.ilike(code),
            ).first()
            if duplicate_code:
                return jsonify({"error": "Warehouse with this code already exists"}), 400
            warehouse.code = code

        if "address" in data:
            warehouse.address = data.get("address")
        if "city" in data:
            warehouse.city = data.get("city")
        if "state" in data:
            warehouse.state = data.get("state")
        if "country" in data:
            warehouse.country = data.get("country")
        if "postal_code" in data:
            warehouse.postal_code = data.get("postal_code")
        if "phone" in data:
            warehouse.phone = data.get("phone")
        if "is_active" in data:
            warehouse.is_active = bool(data.get("is_active"))

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Warehouse updated successfully",
                    "warehouse": warehouse.to_dict(),
                }
            ),
            200,
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Failed to update warehouse", "details": str(exc)}), 500


@inventory_bp.route("/warehouses/<int:warehouse_id>", methods=["DELETE"])
@token_required
def delete_warehouse(warehouse_id):
    """Soft-delete warehouse by setting is_active=False."""
    try:
        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        warehouse.is_active = False
        db.session.commit()

        return jsonify({"message": "Warehouse deactivated successfully"}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Failed to delete warehouse", "details": str(exc)}), 500


@inventory_bp.route("/stocks", methods=["GET"])
def list_stocks():
    """List stock with optional product and warehouse filters."""
    product_id = request.args.get("product_id")
    warehouse_id = request.args.get("warehouse_id")
    low_stock = _parse_bool(request.args.get("low_stock"))

    query = Stock.query

    if product_id is not None:
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return jsonify({"error": "product_id must be a valid integer"}), 400
        query = query.filter(Stock.product_id == product_id)

    if warehouse_id is not None:
        try:
            warehouse_id = int(warehouse_id)
        except (TypeError, ValueError):
            return jsonify({"error": "warehouse_id must be a valid integer"}), 400
        query = query.filter(Stock.warehouse_id == warehouse_id)

    stocks = query.order_by(Stock.id.asc()).all()

    if low_stock is True:
        stocks = [stock for stock in stocks if stock.product and stock.product.is_low_stock]

    return jsonify({"stocks": [stock.to_dict() for stock in stocks], "count": len(stocks)}), 200


@inventory_bp.route("/stocks/movements", methods=["GET"])
def list_stock_movements():
    """List stock movement records with optional filtering."""
    product_id = request.args.get("product_id")
    warehouse_id = request.args.get("warehouse_id")
    movement_type = request.args.get("movement_type")

    query = StockMovement.query

    if product_id is not None:
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return jsonify({"error": "product_id must be a valid integer"}), 400
        query = query.filter(StockMovement.product_id == product_id)

    if warehouse_id is not None:
        try:
            warehouse_id = int(warehouse_id)
        except (TypeError, ValueError):
            return jsonify({"error": "warehouse_id must be a valid integer"}), 400
        query = query.filter(StockMovement.warehouse_id == warehouse_id)

    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type.upper())

    movements = query.order_by(StockMovement.created_at.desc()).all()
    return (
        jsonify(
            {
                "movements": [movement.to_dict() for movement in movements],
                "count": len(movements),
            }
        ),
        200,
    )


@inventory_bp.route("/stocks/movement", methods=["POST"])
@token_required
def create_stock_movement():
    """Create stock movement and update stock balances."""
    try:
        data = request.get_json() or {}

        required_fields = ["product_id", "warehouse_id", "movement_type", "quantity"]
        for field in required_fields:
            if data.get(field) in (None, ""):
                return jsonify({"error": f"{field} is required"}), 400

        product_id = _parse_positive_int(data.get("product_id"), "product_id")
        warehouse_id = _parse_positive_int(data.get("warehouse_id"), "warehouse_id")
        movement_type = str(data.get("movement_type")).upper().strip()

        allowed_types = {"IN", "OUT", "ADJUSTMENT", "TRANSFER"}
        if movement_type not in allowed_types:
            return (
                jsonify(
                    {
                        "error": "movement_type must be one of IN, OUT, ADJUSTMENT, TRANSFER"
                    }
                ),
                400,
            )

        quantity_raw = _parse_int(data.get("quantity"), "quantity")
        if movement_type == "ADJUSTMENT":
            if quantity_raw == 0:
                return jsonify({"error": "quantity cannot be 0 for ADJUSTMENT"}), 400
        else:
            if quantity_raw <= 0:
                return jsonify({"error": "quantity must be greater than 0"}), 400

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        to_warehouse = None
        if movement_type == "TRANSFER":
            to_warehouse_id = data.get("to_warehouse_id")
            if to_warehouse_id in (None, ""):
                return jsonify({"error": "to_warehouse_id is required for TRANSFER"}), 400

            to_warehouse_id = _parse_positive_int(to_warehouse_id, "to_warehouse_id")
            if to_warehouse_id == warehouse_id:
                return jsonify({"error": "Transfer source and destination cannot be same"}), 400

            to_warehouse = Warehouse.query.get(to_warehouse_id)
            if not to_warehouse:
                return jsonify({"error": "Destination warehouse not found"}), 404

        user = get_current_user()
        user_id = user.id if user else None

        source_stock = _get_or_create_stock(product_id, warehouse_id)
        reference_type = data.get("reference_type")
        reference_id = data.get("reference_id")
        notes = data.get("notes")

        created_movements = []

        if movement_type == "IN":
            source_stock.quantity += quantity_raw

        elif movement_type == "OUT":
            if source_stock.quantity < quantity_raw:
                return jsonify({"error": "Insufficient stock for OUT movement"}), 400
            source_stock.quantity -= quantity_raw

        elif movement_type == "ADJUSTMENT":
            new_quantity = source_stock.quantity + quantity_raw
            if new_quantity < 0:
                return jsonify({"error": "Adjustment would result in negative stock"}), 400
            source_stock.quantity = new_quantity

        elif movement_type == "TRANSFER":
            if source_stock.quantity < quantity_raw:
                return jsonify({"error": "Insufficient stock for TRANSFER movement"}), 400

            destination_stock = _get_or_create_stock(product_id, to_warehouse.id)
            source_stock.quantity -= quantity_raw
            destination_stock.quantity += quantity_raw

            transfer_out = StockMovement(
                product_id=product_id,
                warehouse_id=warehouse_id,
                movement_type="TRANSFER",
                quantity=quantity_raw,
                reference_type=reference_type,
                reference_id=reference_id,
                notes=notes,
                user_id=user_id,
            )
            transfer_in = StockMovement(
                product_id=product_id,
                warehouse_id=to_warehouse.id,
                movement_type="TRANSFER",
                quantity=quantity_raw,
                reference_type=reference_type,
                reference_id=reference_id,
                notes=notes,
                user_id=user_id,
            )

            db.session.add(transfer_out)
            db.session.add(transfer_in)
            created_movements.extend([transfer_out, transfer_in])

        if movement_type in {"IN", "OUT", "ADJUSTMENT"}:
            movement = StockMovement(
                product_id=product_id,
                warehouse_id=warehouse_id,
                movement_type=movement_type,
                quantity=quantity_raw,
                reference_type=reference_type,
                reference_id=reference_id,
                notes=notes,
                user_id=user_id,
            )
            db.session.add(movement)
            created_movements.append(movement)

        db.session.commit()

        payload = {
            "message": "Stock movement recorded successfully",
            "movement_count": len(created_movements),
            "movements": [movement.to_dict() for movement in created_movements],
            "source_stock": source_stock.to_dict(),
        }

        if movement_type == "TRANSFER":
            destination_stock = Stock.query.filter_by(
                product_id=product_id,
                warehouse_id=to_warehouse.id,
            ).first()
            payload["destination_stock"] = destination_stock.to_dict()

        return jsonify(payload), 201

    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Failed to record stock movement", "details": str(exc)}), 500
