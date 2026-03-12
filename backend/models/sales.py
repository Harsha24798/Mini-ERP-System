"""
Sales Management Models
Handles customers, sales orders, invoices, and payments
"""

from extensions import db
from models.base import TimestampMixin
from sqlalchemy import CheckConstraint


class Customer(db.Model, TimestampMixin):
    """Customer model"""

    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    customer_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(200), nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)  # VAT/GST number

    # Billing address
    billing_address = db.Column(db.Text, nullable=True)
    billing_city = db.Column(db.String(100), nullable=True)
    billing_state = db.Column(db.String(100), nullable=True)
    billing_country = db.Column(db.String(100), nullable=True)
    billing_postal_code = db.Column(db.String(20), nullable=True)

    # Shipping address
    shipping_address = db.Column(db.Text, nullable=True)
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_state = db.Column(db.String(100), nullable=True)
    shipping_country = db.Column(db.String(100), nullable=True)
    shipping_postal_code = db.Column(db.String(20), nullable=True)

    credit_limit = db.Column(db.Numeric(10, 2), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    sales_orders = db.relationship(
        "SalesOrder", back_populates="customer", lazy="dynamic"
    )
    invoices = db.relationship("Invoice", back_populates="customer", lazy="dynamic")

    def __repr__(self):
        return f"<Customer {self.name}>"

    def to_dict(self):
        """Convert customer to dictionary"""
        return {
            "id": self.id,
            "customer_code": self.customer_code,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "tax_id": self.tax_id,
            "billing_address": self.billing_address,
            "billing_city": self.billing_city,
            "billing_state": self.billing_state,
            "billing_country": self.billing_country,
            "billing_postal_code": self.billing_postal_code,
            "shipping_address": self.shipping_address,
            "shipping_city": self.shipping_city,
            "shipping_state": self.shipping_state,
            "shipping_country": self.shipping_country,
            "shipping_postal_code": self.shipping_postal_code,
            "credit_limit": float(self.credit_limit) if self.credit_limit else None,
            "is_active": self.is_active,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class SalesOrder(db.Model, TimestampMixin):
    """Sales order model"""

    __tablename__ = "sales_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    status = db.Column(
        db.String(20), nullable=False, default="draft"
    )  # draft, confirmed, shipped, delivered, cancelled
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True)

    # Financial fields
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    # Additional info
    notes = db.Column(db.Text, nullable=True)
    shipping_address = db.Column(db.Text, nullable=True)
    delivery_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # Created by user

    # Relationships
    customer = db.relationship("Customer", back_populates="sales_orders")
    warehouse = db.relationship("Warehouse")
    items = db.relationship(
        "SalesOrderItem", back_populates="sales_order", cascade="all, delete-orphan"
    )
    invoice = db.relationship("Invoice", back_populates="sales_order", uselist=False)
    user = db.relationship("User")

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="check_so_subtotal_positive"),
        CheckConstraint("tax_amount >= 0", name="check_so_tax_positive"),
        CheckConstraint("discount_amount >= 0", name="check_so_discount_positive"),
        CheckConstraint("total_amount >= 0", name="check_so_total_positive"),
    )

    def __repr__(self):
        return f"<SalesOrder {self.order_number}>"

    def calculate_totals(self):
        """Calculate order totals based on items"""
        self.subtotal = sum(item.line_total for item in self.items)
        self.total_amount = (
            self.subtotal + self.tax_amount - self.discount_amount + self.shipping_cost
        )

    def to_dict(self):
        """Convert sales order to dictionary"""
        return {
            "id": self.id,
            "order_number": self.order_number,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else None,
            "order_date": self.order_date.isoformat(),
            "status": self.status,
            "warehouse_id": self.warehouse_id,
            "subtotal": float(self.subtotal),
            "tax_amount": float(self.tax_amount),
            "discount_amount": float(self.discount_amount),
            "shipping_cost": float(self.shipping_cost),
            "total_amount": float(self.total_amount),
            "notes": self.notes,
            "shipping_address": self.shipping_address,
            "delivery_date": (
                self.delivery_date.isoformat() if self.delivery_date else None
            ),
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class SalesOrderItem(db.Model, TimestampMixin):
    """Sales order item model"""

    __tablename__ = "sales_order_items"

    id = db.Column(db.Integer, primary_key=True)
    sales_order_id = db.Column(
        db.Integer, db.ForeignKey("sales_orders.id"), nullable=False
    )
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percent = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    sales_order = db.relationship("SalesOrder", back_populates="items")
    product = db.relationship("Product")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_so_item_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="check_so_item_price_positive"),
        CheckConstraint(
            "discount_percent >= 0 AND discount_percent <= 100",
            name="check_so_item_discount_valid",
        ),
    )

    def __repr__(self):
        return f"<SalesOrderItem Order:{self.sales_order_id} Product:{self.product_id}>"

    def calculate_line_total(self):
        """Calculate line total with discount"""
        from decimal import Decimal

        discount_percent = (
            self.discount_percent if self.discount_percent is not None else Decimal("0")
        )
        discount = self.unit_price * self.quantity * (discount_percent / Decimal("100"))
        self.line_total = (self.unit_price * self.quantity) - discount

    def to_dict(self):
        """Convert sales order item to dictionary"""
        return {
            "id": self.id,
            "sales_order_id": self.sales_order_id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "product_sku": self.product.sku if self.product else None,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "discount_percent": float(self.discount_percent),
            "line_total": float(self.line_total),
            "created_at": self.created_at.isoformat(),
        }


class Invoice(db.Model, TimestampMixin):
    """Invoice model"""

    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    sales_order_id = db.Column(
        db.Integer, db.ForeignKey("sales_orders.id"), nullable=False
    )
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    invoice_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(
        db.String(20), nullable=False, default="unpaid"
    )  # unpaid, partial, paid, overdue, cancelled

    # Financial fields
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    balance_due = db.Column(db.Numeric(10, 2), nullable=False)

    notes = db.Column(db.Text, nullable=True)

    # Relationships
    sales_order = db.relationship("SalesOrder", back_populates="invoice")
    customer = db.relationship("Customer", back_populates="invoices")
    payments = db.relationship(
        "Payment", back_populates="invoice", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"

    def update_balance(self):
        """Update balance after payment"""
        self.paid_amount = sum(
            payment.amount for payment in self.payments if payment.status == "completed"
        )
        self.balance_due = self.total_amount - self.paid_amount

        # Update status
        if self.balance_due == 0:
            self.status = "paid"
        elif self.paid_amount > 0:
            self.status = "partial"
        else:
            self.status = "unpaid"

    def to_dict(self):
        """Convert invoice to dictionary"""
        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "sales_order_id": self.sales_order_id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else None,
            "invoice_date": self.invoice_date.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "subtotal": float(self.subtotal),
            "tax_amount": float(self.tax_amount),
            "discount_amount": float(self.discount_amount),
            "total_amount": float(self.total_amount),
            "paid_amount": float(self.paid_amount),
            "balance_due": float(self.balance_due),
            "notes": self.notes,
            "payments": [payment.to_dict() for payment in self.payments],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Payment(db.Model, TimestampMixin):
    """Payment model for tracking invoice payments"""

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(
        db.String(50), nullable=False
    )  # cash, card, bank_transfer, cheque
    reference = db.Column(db.String(100), nullable=True)  # Transaction reference
    status = db.Column(
        db.String(20), nullable=False, default="completed"
    )  # pending, completed, failed
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    invoice = db.relationship("Invoice", back_populates="payments")
    user = db.relationship("User")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_payment_amount_positive"),
    )

    def __repr__(self):
        return f"<Payment {self.payment_number}>"

    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            "id": self.id,
            "payment_number": self.payment_number,
            "invoice_id": self.invoice_id,
            "payment_date": self.payment_date.isoformat(),
            "amount": float(self.amount),
            "payment_method": self.payment_method,
            "reference": self.reference,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }
