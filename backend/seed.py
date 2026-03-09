"""
Database seeding script
Populates database with sample data for development and testing
"""
from app import create_app, db
from models import (
    User, Role, Permission,
    Category, Product, Warehouse, Stock,
    Customer, Supplier
)
from datetime import datetime, timedelta
import random


def seed_permissions():
    """Create default permissions"""
    print("Creating permissions...")
    permissions_data = [
        # User management
        {'name': 'user.create', 'resource': 'user', 'action': 'create', 'description': 'Create users'},
        {'name': 'user.read', 'resource': 'user', 'action': 'read', 'description': 'View users'},
        {'name': 'user.update', 'resource': 'user', 'action': 'update', 'description': 'Update users'},
        {'name': 'user.delete', 'resource': 'user', 'action': 'delete', 'description': 'Delete users'},
        
        # Product management
        {'name': 'product.create', 'resource': 'product', 'action': 'create', 'description': 'Create products'},
        {'name': 'product.read', 'resource': 'product', 'action': 'read', 'description': 'View products'},
        {'name': 'product.update', 'resource': 'product', 'action': 'update', 'description': 'Update products'},
        {'name': 'product.delete', 'resource': 'product', 'action': 'delete', 'description': 'Delete products'},
        
        # Sales management
        {'name': 'sales.create', 'resource': 'sales', 'action': 'create', 'description': 'Create sales orders'},
        {'name': 'sales.read', 'resource': 'sales', 'action': 'read', 'description': 'View sales orders'},
        {'name': 'sales.update', 'resource': 'sales', 'action': 'update', 'description': 'Update sales orders'},
        {'name': 'sales.delete', 'resource': 'sales', 'action': 'delete', 'description': 'Delete sales orders'},
        
        # Purchase management
        {'name': 'purchase.create', 'resource': 'purchase', 'action': 'create', 'description': 'Create purchase orders'},
        {'name': 'purchase.read', 'resource': 'purchase', 'action': 'read', 'description': 'View purchase orders'},
        {'name': 'purchase.update', 'resource': 'purchase', 'action': 'update', 'description': 'Update purchase orders'},
        {'name': 'purchase.delete', 'resource': 'purchase', 'action': 'delete', 'description': 'Delete purchase orders'},
        
        # Reports
        {'name': 'reports.view', 'resource': 'reports', 'action': 'read', 'description': 'View reports'},
    ]
    
    permissions = []
    for perm_data in permissions_data:
        permission = Permission.query.filter_by(name=perm_data['name']).first()
        if not permission:
            permission = Permission(**perm_data)
            db.session.add(permission)
            permissions.append(permission)
    
    db.session.commit()
    print(f"✓ Created {len(permissions)} permissions")
    return Permission.query.all()


def seed_roles(permissions):
    """Create default roles with permissions"""
    print("Creating roles...")
    
    # Admin role - all permissions
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        admin_role = Role(name='Admin', description='Administrator with full access')
        for perm in permissions:
            admin_role.permissions.append(perm)
        db.session.add(admin_role)
    
    # Manager role - most permissions except user management
    manager_role = Role.query.filter_by(name='Manager').first()
    if not manager_role:
        manager_role = Role(name='Manager', description='Manager with business operations access')
        manager_perms = [p for p in permissions if not p.resource == 'user']
        for perm in manager_perms:
            manager_role.permissions.append(perm)
        db.session.add(manager_role)
    
    # Staff role - read access and basic operations
    staff_role = Role.query.filter_by(name='Staff').first()
    if not staff_role:
        staff_role = Role(name='Staff', description='Staff with limited access')
        staff_perms = [p for p in permissions if p.action == 'read' or (p.resource in ['sales', 'purchase'] and p.action == 'create')]
        for perm in staff_perms:
            staff_role.permissions.append(perm)
        db.session.add(staff_role)
    
    db.session.commit()
    print(f"✓ Created roles: Admin, Manager, Staff")
    return {'admin': admin_role, 'manager': manager_role, 'staff': staff_role}


def seed_users(roles):
    """Create default users"""
    print("Creating users...")
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@minierp.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_admin': True,
            'role': 'admin'
        },
        {
            'username': 'manager',
            'email': 'manager@minierp.com',
            'password': 'manager123',
            'first_name': 'Manager',
            'last_name': 'User',
            'is_admin': False,
            'role': 'manager'
        },
        {
            'username': 'staff',
            'email': 'staff@minierp.com',
            'password': 'staff123',
            'first_name': 'Staff',
            'last_name': 'User',
            'is_admin': False,
            'role': 'staff'
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User.query.filter_by(username=user_data['username']).first()
        if not user:
            role_name = user_data.pop('role')
            password = user_data.pop('password')
            
            user = User(**user_data)
            user.set_password(password)
            user.roles.append(roles[role_name])
            
            db.session.add(user)
            users.append(user)
    
    db.session.commit()
    print(f"✓ Created {len(users)} users (admin, manager, staff)")


def seed_categories():
    """Create product categories"""
    print("Creating categories...")
    
    categories_data = [
        {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
        {'name': 'Computers', 'description': 'Computers and computer accessories'},
        {'name': 'Office Supplies', 'description': 'Office and stationery supplies'},
        {'name': 'Furniture', 'description': 'Office and home furniture'},
        {'name': 'Software', 'description': 'Software and licenses'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category.query.filter_by(name=cat_data['name']).first()
        if not category:
            category = Category(**cat_data)
            db.session.add(category)
            categories.append(category)
    
    db.session.commit()
    print(f"✓ Created {len(categories)} categories")
    return Category.query.all()


def seed_warehouses():
    """Create warehouses"""
    print("Creating warehouses...")
    
    warehouses_data = [
        {
            'name': 'Main Warehouse',
            'code': 'WH-01',
            'address': '123 Industrial Area',
            'city': 'New York',
            'state': 'NY',
            'country': 'USA',
            'postal_code': '10001',
            'phone': '+1-212-555-0001'
        },
        {
            'name': 'East Warehouse',
            'code': 'WH-02',
            'address': '456 Storage Lane',
            'city': 'Boston',
            'state': 'MA',
            'country': 'USA',
            'postal_code': '02101',
            'phone': '+1-617-555-0002'
        }
    ]
    
    warehouses = []
    for wh_data in warehouses_data:
        warehouse = Warehouse.query.filter_by(code=wh_data['code']).first()
        if not warehouse:
            warehouse = Warehouse(**wh_data)
            db.session.add(warehouse)
            warehouses.append(warehouse)
    
    db.session.commit()
    print(f"✓ Created {len(warehouses)} warehouses")
    return Warehouse.query.all()


def seed_products(categories, warehouses):
    """Create products with stock"""
    print("Creating products...")
    
    products_data = [
        {'sku': 'LAPTOP-001', 'name': 'Dell Laptop XPS 15', 'category': 'Computers', 'price': 1299.99, 'cost': 999.99, 'unit': 'pcs'},
        {'sku': 'LAPTOP-002', 'name': 'HP Laptop ProBook', 'category': 'Computers', 'price': 899.99, 'cost': 699.99, 'unit': 'pcs'},
        {'sku': 'MOUSE-001', 'name': 'Logitech Wireless Mouse', 'category': 'Electronics', 'price': 29.99, 'cost': 19.99, 'unit': 'pcs'},
        {'sku': 'KEYB-001', 'name': 'Mechanical Keyboard RGB', 'category': 'Electronics', 'price': 89.99, 'cost': 59.99, 'unit': 'pcs'},
        {'sku': 'MONITOR-001', 'name': '27" 4K Monitor Dell', 'category': 'Computers', 'price': 449.99, 'cost': 349.99, 'unit': 'pcs'},
        {'sku': 'CHAIR-001', 'name': 'Ergonomic Office Chair', 'category': 'Furniture', 'price': 299.99, 'cost': 199.99, 'unit': 'pcs'},
        {'sku': 'DESK-001', 'name': 'Standing Desk Adjustable', 'category': 'Furniture', 'price': 599.99, 'cost': 399.99, 'unit': 'pcs'},
        {'sku': 'PAPER-001', 'name': 'A4 Paper Ream (500 sheets)', 'category': 'Office Supplies', 'price': 5.99, 'cost': 3.99, 'unit': 'ream'},
        {'sku': 'PEN-001', 'name': 'Ballpoint Pens Box (50 pcs)', 'category': 'Office Supplies', 'price': 12.99, 'cost': 8.99, 'unit': 'box'},
        {'sku': 'HEADSET-001', 'name': 'Wireless Headset with Mic', 'category': 'Electronics', 'price': 79.99, 'cost': 49.99, 'unit': 'pcs'},
    ]
    
    products = []
    for prod_data in products_data:
        product = Product.query.filter_by(sku=prod_data['sku']).first()
        if not product:
            category_name = prod_data.pop('category')
            category = next((c for c in categories if c.name == category_name), categories[0])
            
            product = Product(**prod_data, category_id=category.id)
            db.session.add(product)
            products.append(product)
    
    db.session.commit()
    
    # Add stock for products
    print("Creating stock records...")
    for product in products:
        for warehouse in warehouses:
            stock = Stock.query.filter_by(product_id=product.id, warehouse_id=warehouse.id).first()
            if not stock:
                quantity = random.randint(10, 100)
                stock = Stock(product_id=product.id, warehouse_id=warehouse.id, quantity=quantity)
                db.session.add(stock)
    
    db.session.commit()
    print(f"✓ Created {len(products)} products with stock")


def seed_customers():
    """Create customers"""
    print("Creating customers...")
    
    customers_data = [
        {
            'customer_code': 'CUST-001',
            'name': 'John Smith',
            'email': 'john.smith@example.com',
            'phone': '+1-555-0101',
            'company': 'Tech Solutions Inc.',
            'billing_address': '789 Business Ave',
            'billing_city': 'New York',
            'billing_state': 'NY',
            'billing_country': 'USA',
            'billing_postal_code': '10002'
        },
        {
            'customer_code': 'CUST-002',
            'name': 'Sarah Johnson',
            'email': 'sarah.j@example.com',
            'phone': '+1-555-0102',
            'company': 'Design Studio LLC',
            'billing_address': '321 Creative St',
            'billing_city': 'Los Angeles',
            'billing_state': 'CA',
            'billing_country': 'USA',
            'billing_postal_code': '90001'
        },
        {
            'customer_code': 'CUST-003',
            'name': 'Michael Brown',
            'email': 'mbrown@example.com',
            'phone': '+1-555-0103',
            'company': 'Global Enterprises',
            'billing_address': '555 Commerce Blvd',
            'billing_city': 'Chicago',
            'billing_state': 'IL',
            'billing_country': 'USA',
            'billing_postal_code': '60601'
        }
    ]
    
    customers = []
    for cust_data in customers_data:
        customer = Customer.query.filter_by(customer_code=cust_data['customer_code']).first()
        if not customer:
            customer = Customer(**cust_data)
            db.session.add(customer)
            customers.append(customer)
    
    db.session.commit()
    print(f"✓ Created {len(customers)} customers")


def seed_suppliers():
    """Create suppliers"""
    print("Creating suppliers...")
    
    suppliers_data = [
        {
            'supplier_code': 'SUP-001',
            'name': 'TechWare Distributors',
            'email': 'info@techware.com',
            'phone': '+1-555-0201',
            'company': 'TechWare Distributors Inc.',
            'address': '100 Supply Chain Road',
            'city': 'San Francisco',
            'state': 'CA',
            'country': 'USA',
            'postal_code': '94101',
            'payment_terms': 'Net 30'
        },
        {
            'supplier_code': 'SUP-002',
            'name': 'Office Supplies Co',
            'email': 'sales@officesupplies.com',
            'phone': '+1-555-0202',
            'company': 'Office Supplies Co',
            'address': '200 Wholesale Ave',
            'city': 'Seattle',
            'state': 'WA',
            'country': 'USA',
            'postal_code': '98101',
            'payment_terms': 'Net 60'
        }
    ]
    
    suppliers = []
    for supp_data in suppliers_data:
        supplier = Supplier.query.filter_by(supplier_code=supp_data['supplier_code']).first()
        if not supplier:
            supplier = Supplier(**supp_data)
            db.session.add(supplier)
            suppliers.append(supplier)
    
    db.session.commit()
    print(f"✓ Created {len(suppliers)} suppliers")


def seed_all():
    """Seed all data"""
    print("\n" + "="*50)
    print("Starting database seeding...")
    print("="*50 + "\n")
    
    try:
        # Seed in order due to dependencies
        permissions = seed_permissions()
        roles = seed_roles(permissions)
        seed_users(roles)
        categories = seed_categories()
        warehouses = seed_warehouses()
        seed_products(categories, warehouses)
        seed_customers()
        seed_suppliers()
        
        print("\n" + "="*50)
        print("✓ Database seeding completed successfully!")
        print("="*50 + "\n")
        
        print("Default Users Created:")
        print("  - Admin:   username: admin   | password: admin123")
        print("  - Manager: username: manager | password: manager123")
        print("  - Staff:   username: staff   | password: staff123")
        print()
        
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Error during seeding: {e}")
        raise


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_all()
