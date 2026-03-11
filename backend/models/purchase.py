"""
Purchase Management Models
Handles suppliers, purchase orders, and bills
"""
from extensions import db
from models.base import TimestampMixin
from sqlalchemy import CheckConstraint


class Supplier(db.Model, TimestampMixin):
    """Supplier model"""
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    supplier_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(200), nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)  # VAT/GST number
    
    # Address
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    
    # Bank details
    bank_name = db.Column(db.String(100), nullable=True)
    bank_account = db.Column(db.String(50), nullable=True)
    
    payment_terms = db.Column(db.String(100), nullable=True)  # e.g., "Net 30", "Net 60"
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    purchase_orders = db.relationship('PurchaseOrder', back_populates='supplier', lazy='dynamic')
    bills = db.relationship('Bill', back_populates='supplier', lazy='dynamic')

    def __repr__(self):
        return f'<Supplier {self.name}>'

    def to_dict(self):
        """Convert supplier to dictionary"""
        return {
            'id': self.id,
            'supplier_code': self.supplier_code,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'tax_id': self.tax_id,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'bank_name': self.bank_name,
            'bank_account': self.bank_account,
            'payment_terms': self.payment_terms,
            'is_active': self.is_active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class PurchaseOrder(db.Model, TimestampMixin):
    """Purchase order model"""
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, sent, received, completed, cancelled
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True)
    expected_date = db.Column(db.DateTime, nullable=True)
    
    # Financial fields
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    
    # Additional info
    notes = db.Column(db.Text, nullable=True)
    received_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Created by user
    
    # Relationships
    supplier = db.relationship('Supplier', back_populates='purchase_orders')
    warehouse = db.relationship('Warehouse')
    items = db.relationship('PurchaseOrderItem', back_populates='purchase_order', cascade='all, delete-orphan')
    bill = db.relationship('Bill', back_populates='purchase_order', uselist=False)
    user = db.relationship('User')

    __table_args__ = (
        CheckConstraint('subtotal >= 0', name='check_po_subtotal_positive'),
        CheckConstraint('tax_amount >= 0', name='check_po_tax_positive'),
        CheckConstraint('discount_amount >= 0', name='check_po_discount_positive'),
        CheckConstraint('total_amount >= 0', name='check_po_total_positive'),
    )

    def __repr__(self):
        return f'<PurchaseOrder {self.order_number}>'

    def calculate_totals(self):
        """Calculate order totals based on items"""
        self.subtotal = sum(item.line_total for item in self.items)
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount + self.shipping_cost

    def to_dict(self):
        """Convert purchase order to dictionary"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'order_date': self.order_date.isoformat(),
            'status': self.status,
            'warehouse_id': self.warehouse_id,
            'expected_date': self.expected_date.isoformat() if self.expected_date else None,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'shipping_cost': float(self.shipping_cost),
            'total_amount': float(self.total_amount),
            'notes': self.notes,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class PurchaseOrderItem(db.Model, TimestampMixin):
    """Purchase order item model"""
    __tablename__ = 'purchase_order_items'

    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percent = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)
    received_quantity = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationships
    purchase_order = db.relationship('PurchaseOrder', back_populates='items')
    product = db.relationship('Product')

    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_po_item_quantity_positive'),
        CheckConstraint('unit_cost >= 0', name='check_po_item_cost_positive'),
        CheckConstraint('discount_percent >= 0 AND discount_percent <= 100', name='check_po_item_discount_valid'),
        CheckConstraint('received_quantity >= 0', name='check_po_item_received_positive'),
    )

    def __repr__(self):
        return f'<PurchaseOrderItem Order:{self.purchase_order_id} Product:{self.product_id}>'

    def calculate_line_total(self):
        """Calculate line total with discount"""
        from decimal import Decimal
        discount_percent = self.discount_percent if self.discount_percent is not None else Decimal('0')
        discount = self.unit_cost * self.quantity * (discount_percent / Decimal('100'))
        self.line_total = (self.unit_cost * self.quantity) - discount

    def to_dict(self):
        """Convert purchase order item to dictionary"""
        return {
            'id': self.id,
            'purchase_order_id': self.purchase_order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'product_sku': self.product.sku if self.product else None,
            'quantity': self.quantity,
            'unit_cost': float(self.unit_cost),
            'discount_percent': float(self.discount_percent),
            'line_total': float(self.line_total),
            'received_quantity': self.received_quantity,
            'created_at': self.created_at.isoformat()
        }


class Bill(db.Model, TimestampMixin):
    """Bill model for supplier invoices"""
    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    bill_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='unpaid')  # unpaid, partial, paid, overdue, cancelled
    
    # Financial fields
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    balance_due = db.Column(db.Numeric(10, 2), nullable=False)
    
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    purchase_order = db.relationship('PurchaseOrder', back_populates='bill')
    supplier = db.relationship('Supplier', back_populates='bills')

    def __repr__(self):
        return f'<Bill {self.bill_number}>'

    def update_balance(self):
        """Update balance after payment"""
        # Note: Payment tracking for bills can be added similar to invoices
        self.balance_due = self.total_amount - self.paid_amount
        
        # Update status
        if self.balance_due == 0:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'unpaid'

    def to_dict(self):
        """Convert bill to dictionary"""
        return {
            'id': self.id,
            'bill_number': self.bill_number,
            'purchase_order_id': self.purchase_order_id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'bill_date': self.bill_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'paid_amount': float(self.paid_amount),
            'balance_due': float(self.balance_due),
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
