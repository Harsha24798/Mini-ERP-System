"""
Unit tests for purchase models
"""
import pytest
from models import Supplier, PurchaseOrder, PurchaseOrderItem, Bill, Product, Category, Warehouse, User
from extensions import db
from decimal import Decimal
from datetime import datetime, timedelta


class TestSupplierModel:
    """Tests for Supplier model"""
    
    def test_create_supplier(self, db_session):
        """Test creating a supplier"""
        supplier = Supplier(
            supplier_code='SUP-TEST-001',
            name='Test Supplier',
            email='supplier@test.com',
            phone='+1-555-0001',
            company='Test Supplier Inc',
            payment_terms='Net 30'
        )
        db_session.add(supplier)
        db_session.commit()
        
        assert supplier.id is not None
        assert supplier.supplier_code == 'SUP-TEST-001'
        assert supplier.name == 'Test Supplier'
        assert supplier.payment_terms == 'Net 30'


class TestPurchaseOrderModel:
    """Tests for PurchaseOrder model"""
    
    def test_create_purchase_order(self, db_session):
        """Test creating a purchase order"""
        supplier = Supplier(supplier_code='SUP-001', name='Supplier One', email='s1@test.com')
        warehouse = Warehouse(name='Main WH', code='MAIN')
        user = User(username='purchuser', email='purch@test.com', first_name='Purchase', last_name='User')
        user.set_password('password')
        
        db_session.add_all([supplier, warehouse, user])
        db_session.commit()
        
        po = PurchaseOrder(
            order_number='PO-001',
            supplier_id=supplier.id,
            warehouse_id=warehouse.id,
            status='draft',
            subtotal=Decimal('500.00'),
            total_amount=Decimal('500.00'),
            user_id=user.id
        )
        db_session.add(po)
        db_session.commit()
        
        assert po.id is not None
        assert po.order_number == 'PO-001'
        assert po.status == 'draft'
    
    def test_purchase_order_calculate_totals(self, db_session):
        """Test purchase order total calculation"""
        supplier = Supplier(supplier_code='SUP-002', name='Supplier Two', email='s2@test.com')
        category = Category(name='Parts')
        db_session.add_all([supplier, category])
        db_session.commit()
        
        product1 = Product(sku='PART1', name='Part 1', category_id=category.id, price=Decimal('50.00'), cost=Decimal('30.00'))
        product2 = Product(sku='PART2', name='Part 2', category_id=category.id, price=Decimal('80.00'), cost=Decimal('50.00'))
        db_session.add_all([product1, product2])
        db_session.commit()
        
        po = PurchaseOrder(
            order_number='PO-002',
            supplier_id=supplier.id,
            status='draft',
            subtotal=Decimal('0'),
            total_amount=Decimal('0')
        )
        db_session.add(po)
        db_session.commit()
        
        # Add PO items
        item1 = PurchaseOrderItem(
            purchase_order_id=po.id,
            product_id=product1.id,
            quantity=10,
            unit_cost=product1.cost,
            line_total=Decimal('300.00')
        )
        item2 = PurchaseOrderItem(
            purchase_order_id=po.id,
            product_id=product2.id,
            quantity=5,
            unit_cost=product2.cost,
            line_total=Decimal('250.00')
        )
        db_session.add_all([item1, item2])
        db_session.commit()
        
        po.calculate_totals()
        db_session.commit()
        
        assert po.subtotal == Decimal('550.00')
        assert po.total_amount == Decimal('550.00')


class TestPurchaseOrderItemModel:
    """Tests for PurchaseOrderItem model"""
    
    def test_calculate_line_total(self, db_session):
        """Test line total calculation with discount"""
        supplier = Supplier(supplier_code='SUP-003', name='Supplier Three', email='s3@test.com')
        category = Category(name='Materials')
        db_session.add_all([supplier, category])
        db_session.commit()
        
        product = Product(sku='MAT-001', name='Material', category_id=category.id, price=Decimal('200.00'), cost=Decimal('120.00'))
        db_session.add(product)
        db_session.commit()
        
        po = PurchaseOrder(
            order_number='PO-003',
            supplier_id=supplier.id,
            status='draft',
            subtotal=Decimal('0'),
            total_amount=Decimal('0')
        )
        db_session.add(po)
        db_session.commit()
        
        item = PurchaseOrderItem(
            purchase_order_id=po.id,
            product_id=product.id,
            quantity=5,
            unit_cost=product.cost,
            discount_percent=Decimal('5.00'),  # 5% discount
            line_total=Decimal('0')
        )
        item.calculate_line_total()
        db_session.add(item)
        db_session.commit()
        
        # 5 * 120 = 600, minus 5% = 570
        assert item.line_total == Decimal('570.00')
    
    def test_track_received_quantity(self, db_session):
        """Test tracking received quantity"""
        supplier = Supplier(supplier_code='SUP-004', name='Supplier Four', email='s4@test.com')
        category = Category(name='Goods')
        db_session.add_all([supplier, category])
        db_session.commit()
        
        product = Product(sku='GOOD-001', name='Good Item', category_id=category.id, price=Decimal('100.00'))
        db_session.add(product)
        db_session.commit()
        
        po = PurchaseOrder(
            order_number='PO-004',
            supplier_id=supplier.id,
            status='sent',
            subtotal=Decimal('1000.00'),
            total_amount=Decimal('1000.00')
        )
        db_session.add(po)
        db_session.commit()
        
        item = PurchaseOrderItem(
            purchase_order_id=po.id,
            product_id=product.id,
            quantity=10,
            unit_cost=Decimal('100.00'),
            received_quantity=0
        )
        item.calculate_line_total()
        db_session.add(item)
        db_session.commit()
        
        # Simulate partial receipt
        item.received_quantity = 5
        db_session.commit()
        
        assert item.received_quantity == 5
        assert item.quantity == 10  # Ordered quantity remains same


class TestBillModel:
    """Tests for Bill model"""
    
    def test_create_bill(self, db_session):
        """Test creating a bill"""
        supplier = Supplier(supplier_code='SUP-005', name='Supplier Five', email='s5@test.com')
        db_session.add(supplier)
        db_session.commit()
        
        po = PurchaseOrder(
            order_number='PO-005',
            supplier_id=supplier.id,
            status='received',
            subtotal=Decimal('700.00'),
            total_amount=Decimal('700.00')
        )
        db_session.add(po)
        db_session.commit()
        
        bill = Bill(
            bill_number='BILL-001',
            purchase_order_id=po.id,
            supplier_id=supplier.id,
            bill_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=60),
            subtotal=Decimal('700.00'),
            total_amount=Decimal('700.00'),
            balance_due=Decimal('700.00'),
            status='unpaid'
        )
        db_session.add(bill)
        db_session.commit()
        
        assert bill.id is not None
        assert bill.bill_number == 'BILL-001'
        assert bill.status == 'unpaid'
    
    def test_bill_update_balance(self, db_session):
        """Test bill balance update"""
        supplier = Supplier(supplier_code='SUP-006', name='Supplier Six', email='s6@test.com')
        db_session.add(supplier)
        db_session.commit()
        
        po = PurchaseOrder(
            order_number='PO-006',
            supplier_id=supplier.id,
            status='received',
            subtotal=Decimal('1000.00'),
            total_amount=Decimal('1000.00')
        )
        db_session.add(po)
        db_session.commit()
        
        bill = Bill(
            bill_number='BILL-002',
            purchase_order_id=po.id,
            supplier_id=supplier.id,
            subtotal=Decimal('1000.00'),
            total_amount=Decimal('1000.00'),
            balance_due=Decimal('1000.00'),
            status='unpaid'
        )
        db_session.add(bill)
        db_session.commit()
        
        # Simulate payment
        bill.paid_amount = Decimal('400.00')
        bill.update_balance()
        db_session.commit()
        
        assert bill.paid_amount == Decimal('400.00')
        assert bill.balance_due == Decimal('600.00')
        assert bill.status == 'partial'
        
        # Pay remaining
        bill.paid_amount = Decimal('1000.00')
        bill.update_balance()
        db_session.commit()
        
        assert bill.balance_due == Decimal('0.00')
        assert bill.status == 'paid'
