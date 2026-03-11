"""
Unit tests for sales models
"""
import pytest
from models import Customer, SalesOrder, SalesOrderItem, Invoice, Payment, Product, Category, Warehouse, User
from extensions import db
from decimal import Decimal
from datetime import datetime, timedelta


class TestCustomerModel:
    """Tests for Customer model"""
    
    def test_create_customer(self, db_session):
        """Test creating a customer"""
        customer = Customer(
            customer_code='CUST-TEST-001',
            name='Test Customer',
            email='customer@test.com',
            phone='+1-555-0001',
            company='Test Company'
        )
        db_session.add(customer)
        db_session.commit()
        
        assert customer.id is not None
        assert customer.customer_code == 'CUST-TEST-001'
        assert customer.name == 'Test Customer'


class TestSalesOrderModel:
    """Tests for SalesOrder model"""
    
    def test_create_sales_order(self, db_session):
        """Test creating a sales order"""
        customer = Customer(customer_code='CUST-001', name='Customer One', email='c1@test.com')
        warehouse = Warehouse(name='Main WH', code='MAIN')
        user = User(username='salesuser', email='sales@test.com', first_name='Sales', last_name='User')
        user.set_password('password')
        
        db_session.add_all([customer, warehouse, user])
        db_session.commit()
        
        order = SalesOrder(
            order_number='SO-001',
            customer_id=customer.id,
            warehouse_id=warehouse.id,
            status='draft',
            subtotal=Decimal('100.00'),
            total_amount=Decimal('100.00'),
            user_id=user.id
        )
        db_session.add(order)
        db_session.commit()
        
        assert order.id is not None
        assert order.order_number == 'SO-001'
        assert order.status == 'draft'
    
    def test_sales_order_calculate_totals(self, db_session):
        """Test sales order total calculation"""
        customer = Customer(customer_code='CUST-002', name='Customer Two', email='c2@test.com')
        category = Category(name='Products')
        db_session.add_all([customer, category])
        db_session.commit()
        
        product1 = Product(sku='P1', name='Product 1', category_id=category.id, price=Decimal('10.00'))
        product2 = Product(sku='P2', name='Product 2', category_id=category.id, price=Decimal('20.00'))
        db_session.add_all([product1, product2])
        db_session.commit()
        
        order = SalesOrder(
            order_number='SO-002',
            customer_id=customer.id,
            status='draft',
            subtotal=Decimal('0'),
            total_amount=Decimal('0')
        )
        db_session.add(order)
        db_session.commit()
        
        # Add order items
        item1 = SalesOrderItem(
            sales_order_id=order.id,
            product_id=product1.id,
            quantity=2,
            unit_price=product1.price,
            line_total=Decimal('20.00')
        )
        item2 = SalesOrderItem(
            sales_order_id=order.id,
            product_id=product2.id,
            quantity=3,
            unit_price=product2.price,
            line_total=Decimal('60.00')
        )
        db_session.add_all([item1, item2])
        db_session.commit()
        
        order.calculate_totals()
        db_session.commit()
        
        assert order.subtotal == Decimal('80.00')
        assert order.total_amount == Decimal('80.00')


class TestSalesOrderItemModel:
    """Tests for SalesOrderItem model"""
    
    def test_calculate_line_total(self, db_session):
        """Test line total calculation with discount"""
        customer = Customer(customer_code='CUST-003', name='Customer Three', email='c3@test.com')
        category = Category(name='Items')
        db_session.add_all([customer, category])
        db_session.commit()
        
        product = Product(sku='DISC-001', name='Discounted Product', category_id=category.id, price=Decimal('100.00'))
        db_session.add(product)
        db_session.commit()
        
        order = SalesOrder(
            order_number='SO-003',
            customer_id=customer.id,
            status='draft',
            subtotal=Decimal('0'),
            total_amount=Decimal('0')
        )
        db_session.add(order)
        db_session.commit()
        
        item = SalesOrderItem(
            sales_order_id=order.id,
            product_id=product.id,
            quantity=2,
            unit_price=product.price,
            discount_percent=Decimal('10.00'),  # 10% discount
            line_total=Decimal('0')
        )
        item.calculate_line_total()
        db_session.add(item)
        db_session.commit()
        
        # 2 * 100 = 200, minus 10% = 180
        assert item.line_total == Decimal('180.00')


class TestInvoiceModel:
    """Tests for Invoice model"""
    
    def test_create_invoice(self, db_session):
        """Test creating an invoice"""
        customer = Customer(customer_code='CUST-004', name='Customer Four', email='c4@test.com')
        db_session.add(customer)
        db_session.commit()
        
        order = SalesOrder(
            order_number='SO-004',
            customer_id=customer.id,
            status='confirmed',
            subtotal=Decimal('200.00'),
            total_amount=Decimal('200.00')
        )
        db_session.add(order)
        db_session.commit()
        
        invoice = Invoice(
            invoice_number='INV-001',
            sales_order_id=order.id,
            customer_id=customer.id,
            invoice_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=30),
            subtotal=Decimal('200.00'),
            total_amount=Decimal('200.00'),
            balance_due=Decimal('200.00'),
            status='unpaid'
        )
        db_session.add(invoice)
        db_session.commit()
        
        assert invoice.id is not None
        assert invoice.invoice_number == 'INV-001'
        assert invoice.status == 'unpaid'
    
    def test_invoice_update_balance(self, db_session):
        """Test invoice balance update after payment"""
        customer = Customer(customer_code='CUST-005', name='Customer Five', email='c5@test.com')
        user = User(username='payuser', email='pay@test.com', first_name='Pay', last_name='User')
        user.set_password('password')
        db_session.add_all([customer, user])
        db_session.commit()
        
        order = SalesOrder(
            order_number='SO-005',
            customer_id=customer.id,
            status='confirmed',
            subtotal=Decimal('300.00'),
            total_amount=Decimal('300.00')
        )
        db_session.add(order)
        db_session.commit()
        
        invoice = Invoice(
            invoice_number='INV-002',
            sales_order_id=order.id,
            customer_id=customer.id,
            subtotal=Decimal('300.00'),
            total_amount=Decimal('300.00'),
            balance_due=Decimal('300.00'),
            status='unpaid'
        )
        db_session.add(invoice)
        db_session.commit()
        
        # Add partial payment
        payment = Payment(
            payment_number='PAY-001',
            invoice_id=invoice.id,
            amount=Decimal('150.00'),
            payment_method='card',
            status='completed',
            user_id=user.id
        )
        db_session.add(payment)
        db_session.commit()
        
        invoice.update_balance()
        db_session.commit()
        
        assert invoice.paid_amount == Decimal('150.00')
        assert invoice.balance_due == Decimal('150.00')
        assert invoice.status == 'partial'
        
        # Add remaining payment
        payment2 = Payment(
            payment_number='PAY-002',
            invoice_id=invoice.id,
            amount=Decimal('150.00'),
            payment_method='bank_transfer',
            status='completed',
            user_id=user.id
        )
        db_session.add(payment2)
        db_session.commit()
        
        invoice.update_balance()
        db_session.commit()
        
        assert invoice.paid_amount == Decimal('300.00')
        assert invoice.balance_due == Decimal('0.00')
        assert invoice.status == 'paid'
