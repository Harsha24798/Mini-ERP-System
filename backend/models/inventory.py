"""
Inventory Management Models
Handles products, categories, stock, and warehouses
"""
from app import db
from models.base import TimestampMixin
from sqlalchemy import CheckConstraint


class Category(db.Model, TimestampMixin):
    """Product category model"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Self-referential relationship for hierarchical categories
    parent = db.relationship('Category', remote_side=[id], backref='subcategories')
    
    # Relationship to products
    products = db.relationship('Product', back_populates='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

    def to_dict(self):
        """Convert category to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Product(db.Model, TimestampMixin):
    """Product model"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    unit = db.Column(db.String(20), nullable=False, default='pcs')  # pcs, kg, ltr, etc.
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=True)  # Purchase cost
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    image_url = db.Column(db.String(255), nullable=True)
    barcode = db.Column(db.String(100), unique=True, nullable=True, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    category = db.relationship('Category', back_populates='products')
    stocks = db.relationship('Stock', back_populates='product', lazy='dynamic')
    stock_movements = db.relationship('StockMovement', back_populates='product', lazy='dynamic')

    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
        CheckConstraint('cost >= 0', name='check_cost_positive'),
        CheckConstraint('reorder_level >= 0', name='check_reorder_level_positive'),
    )

    def __repr__(self):
        return f'<Product {self.name}>'

    @property
    def total_stock(self):
        """Calculate total stock across all warehouses"""
        return sum(stock.quantity for stock in self.stocks)

    @property
    def is_low_stock(self):
        """Check if product is below reorder level"""
        return self.total_stock <= self.reorder_level

    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'unit': self.unit,
            'price': float(self.price),
            'cost': float(self.cost) if self.cost else None,
            'reorder_level': self.reorder_level,
            'image_url': self.image_url,
            'barcode': self.barcode,
            'is_active': self.is_active,
            'total_stock': self.total_stock,
            'is_low_stock': self.is_low_stock,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Warehouse(db.Model, TimestampMixin):
    """Warehouse model for managing storage locations"""
    __tablename__ = 'warehouses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    stocks = db.relationship('Stock', back_populates='warehouse', lazy='dynamic')

    def __repr__(self):
        return f'<Warehouse {self.name}>'

    def to_dict(self):
        """Convert warehouse to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Stock(db.Model, TimestampMixin):
    """Stock model to track product quantities in warehouses"""
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationships
    product = db.relationship('Product', back_populates='stocks')
    warehouse = db.relationship('Warehouse', back_populates='stocks')

    __table_args__ = (
        db.UniqueConstraint('product_id', 'warehouse_id', name='unique_product_warehouse'),
        CheckConstraint('quantity >= 0', name='check_quantity_positive'),
    )

    def __repr__(self):
        return f'<Stock Product:{self.product_id} Warehouse:{self.warehouse_id} Qty:{self.quantity}>'

    def to_dict(self):
        """Convert stock to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'quantity': self.quantity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class StockMovement(db.Model, TimestampMixin):
    """Stock movement model for tracking inventory changes (audit trail)"""
    __tablename__ = 'stock_movements'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # IN, OUT, TRANSFER, ADJUSTMENT
    quantity = db.Column(db.Integer, nullable=False)
    reference_type = db.Column(db.String(50), nullable=True)  # sales_order, purchase_order, etc.
    reference_id = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    product = db.relationship('Product', back_populates='stock_movements')
    warehouse = db.relationship('Warehouse')
    user = db.relationship('User')

    def __repr__(self):
        return f'<StockMovement {self.movement_type} {self.quantity} units>'

    def to_dict(self):
        """Convert stock movement to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'notes': self.notes,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }
