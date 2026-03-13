"""
Inventory Routes
Phase 3 starter endpoints for category and product management.
"""

from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from extensions import db
from models import Category, Product
from utils.auth import token_required


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


def _parse_decimal(value, field_name):
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid decimal value")

    if parsed < 0:
        raise ValueError(f"{field_name} must be greater than or equal to 0")

    return parsed


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
