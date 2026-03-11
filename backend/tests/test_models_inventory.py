"""
Unit tests for inventory models
"""
import pytest
from models import Category, Product, Warehouse, Stock, StockMovement, User
from extensions import db
from decimal import Decimal


class TestCategoryModel:
    """Tests for Category model"""
    
    def test_create_category(self, db_session):
        """Test creating a category"""
        category = Category(name='Electronics', description='Electronic items')
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.name == 'Electronics'
        assert category.is_active is True
    
    def test_category_hierarchy(self, db_session):
        """Test hierarchical categories"""
        parent = Category(name='Computers')
        child = Category(name='Laptops', parent=parent)
        
        db_session.add_all([parent, child])
        db_session.commit()
        
        assert child.parent_id == parent.id
        assert child in parent.subcategories


class TestProductModel:
    """Tests for Product model"""
    
    def test_create_product(self, db_session):
        """Test creating a product"""
        category = Category(name='Gadgets')
        db_session.add(category)
        db_session.commit()
        
        product = Product(
            sku='TEST-001',
            name='Test Product',
            category_id=category.id,
            price=Decimal('99.99'),
            cost=Decimal('49.99'),
            unit='pcs'
        )
        db_session.add(product)
        db_session.commit()
        
        assert product.id is not None
        assert product.sku == 'TEST-001'
        assert product.price == Decimal('99.99')
    
    def test_product_total_stock(self, db_session):
        """Test product total stock calculation"""
        category = Category(name='Hardware')
        db_session.add(category)
        db_session.commit()
        
        product = Product(
            sku='PROD-001',
            name='Widget',
            category_id=category.id,
            price=Decimal('10.00')
        )
        
        warehouse1 = Warehouse(name='WH1', code='WH1')
        warehouse2 = Warehouse(name='WH2', code='WH2')
        db_session.add_all([product, warehouse1, warehouse2])
        db_session.commit()
        
        stock1 = Stock(product_id=product.id, warehouse_id=warehouse1.id, quantity=50)
        stock2 = Stock(product_id=product.id, warehouse_id=warehouse2.id, quantity=30)
        db_session.add_all([stock1, stock2])
        db_session.commit()
        
        assert product.total_stock == 80
    
    def test_product_low_stock_check(self, db_session):
        """Test low stock detection"""
        category = Category(name='Parts')
        db_session.add(category)
        db_session.commit()
        
        product = Product(
            sku='LOW-001',
            name='Low Stock Item',
            category_id=category.id,
            price=Decimal('5.00'),
            reorder_level=20
        )
        
        warehouse = Warehouse(name='Main', code='MAIN')
        db_session.add_all([product, warehouse])
        db_session.commit()
        
        # Add stock below reorder level
        stock = Stock(product_id=product.id, warehouse_id=warehouse.id, quantity=15)
        db_session.add(stock)
        db_session.commit()
        
        assert product.is_low_stock is True


class TestStockModel:
    """Tests for Stock model"""
    
    def test_create_stock(self, db_session):
        """Test creating stock record"""
        category = Category(name='Tools')
        db_session.add(category)
        db_session.commit()
        
        product = Product(sku='TOOL-001', name='Hammer', category_id=category.id, price=Decimal('15.00'))
        warehouse = Warehouse(name='Storage', code='STR')
        db_session.add_all([product, warehouse])
        db_session.commit()
        
        stock = Stock(product_id=product.id, warehouse_id=warehouse.id, quantity=100)
        db_session.add(stock)
        db_session.commit()
        
        assert stock.id is not None
        assert stock.quantity == 100
    
    def test_unique_product_warehouse_constraint(self, db_session):
        """Test that product-warehouse combination must be unique"""
        category = Category(name='Items')
        db_session.add(category)
        db_session.commit()
        
        product = Product(sku='ITEM-001', name='Item', category_id=category.id, price=Decimal('10.00'))
        warehouse = Warehouse(name='WH', code='WH')
        db_session.add_all([product, warehouse])
        db_session.commit()
        
        stock1 = Stock(product_id=product.id, warehouse_id=warehouse.id, quantity=10)
        db_session.add(stock1)
        db_session.commit()
        
        # Trying to add duplicate should fail
        stock2 = Stock(product_id=product.id, warehouse_id=warehouse.id, quantity=20)
        db_session.add(stock2)
        
        with pytest.raises(Exception):
            db_session.commit()
        
        db_session.rollback()


class TestStockMovementModel:
    """Tests for StockMovement model"""
    
    def test_create_stock_movement(self, db_session):
        """Test creating stock movement record"""
        category = Category(name='Supplies')
        db_session.add(category)
        db_session.commit()
        
        product = Product(sku='SUP-001', name='Supply', category_id=category.id, price=Decimal('5.00'))
        warehouse = Warehouse(name='Depot', code='DEP')
        user = User(username='movuser', email='mov@example.com', first_name='Move', last_name='User')
        user.set_password('password')
        
        db_session.add_all([product, warehouse, user])
        db_session.commit()
        
        movement = StockMovement(
            product_id=product.id,
            warehouse_id=warehouse.id,
            movement_type='IN',
            quantity=50,
            reference_type='purchase_order',
            reference_id=1,
            notes='Initial stock',
            user_id=user.id
        )
        db_session.add(movement)
        db_session.commit()
        
        assert movement.id is not None
        assert movement.movement_type == 'IN'
        assert movement.quantity == 50
