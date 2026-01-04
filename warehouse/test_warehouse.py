"""
UNIT TESTS for Warehouse Management System
OOP & VVRPO Course Project - 2024
Comprehensive test suite covering all components
"""

import unittest
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from warehouse_final import (
    # Domain Layer
    Money, Address, ProductCategory, OrderStatus, EmployeeRole,
    Entity, Product, Order, Employee, OrderItem,
    
    # Specialized Products
    ClothingProduct, FoodProduct, BookProduct,
    
    # Design Patterns
    PricingStrategy, RegularPricing, BulkDiscountPricing, SeasonalPricing,
    InventoryObserver, EmailNotifier, LogNotifier,
    ProductFactory, ProductDecorator, DiscountedProduct, FeaturedProduct,
    DatabaseConnection, ReportGenerator, InventoryReportGenerator,
    
    # Use Cases
    UseCase, ProductManagementUseCase,
    
    # Repository Pattern
    Repository, ProductRepository
)

# ==================== TEST VALUE OBJECTS ====================

class TestMoney(unittest.TestCase):
    """Test Money value object"""
    
    def test_money_creation(self):
        """Test creating Money objects"""
        money1 = Money(Decimal('100.50'), 'USD')
        money2 = Money(Decimal('50.25'), 'USD')
        
        self.assertEqual(money1.amount, Decimal('100.50'))
        self.assertEqual(money1.currency, 'USD')
        self.assertEqual(str(money1), 'USD 100.50')
    
    def test_money_addition(self):
        """Test adding Money objects"""
        money1 = Money(Decimal('100'), 'USD')
        money2 = Money(Decimal('50'), 'USD')
        
        result = money1 + money2
        self.assertEqual(result.amount, Decimal('150'))
        self.assertEqual(result.currency, 'USD')
    
    def test_money_addition_different_currency(self):
        """Test adding Money with different currencies should fail"""
        money1 = Money(Decimal('100'), 'USD')
        money2 = Money(Decimal('50'), 'EUR')
        
        with self.assertRaises(ValueError):
            result = money1 + money2
    
    def test_money_multiplication(self):
        """Test multiplying Money by quantity"""
        money = Money(Decimal('25'), 'USD')
        result = money * 4
        
        self.assertEqual(result.amount, Decimal('100'))
        self.assertEqual(result.currency, 'USD')
    
    def test_money_subtraction(self):
        """Test subtracting Money objects"""
        money1 = Money(Decimal('100'), 'USD')
        money2 = Money(Decimal('30'), 'USD')
        
        result = money1 - money2
        self.assertEqual(result.amount, Decimal('70'))
    
    def test_money_division(self):
        """Test dividing Money"""
        money = Money(Decimal('100'), 'USD')
        result = money / 4
        
        self.assertEqual(result.amount, Decimal('25'))
    
    def test_money_division_by_zero(self):
        """Test dividing Money by zero should fail"""
        money = Money(Decimal('100'), 'USD')
        
        with self.assertRaises(ValueError):
            result = money / 0
    
    def test_money_equality(self):
        """Test Money equality"""
        money1 = Money(Decimal('100'), 'USD')
        money2 = Money(Decimal('100'), 'USD')
        money3 = Money(Decimal('100'), 'EUR')
        money4 = Money(Decimal('50'), 'USD')
        
        self.assertEqual(money1, money2)
        self.assertNotEqual(money1, money3)
        self.assertNotEqual(money1, money4)

class TestAddress(unittest.TestCase):
    """Test Address value object"""
    
    def test_address_creation(self):
        """Test creating Address objects"""
        address = Address(
            street="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62704",
            country="USA"
        )
        
        self.assertEqual(address.street, "123 Main St")
        self.assertEqual(address.city, "Springfield")
        self.assertEqual(address.state, "IL")
        self.assertEqual(address.zip_code, "62704")
        self.assertEqual(address.country, "USA")
    
    def test_address_string_representation(self):
        """Test Address string representation"""
        address = Address(
            street="456 Oak Ave",
            city="Chicago",
            state="IL",
            zip_code="60601"
        )
        
        expected = "456 Oak Ave, Chicago, IL 60601, USA"
        self.assertEqual(str(address), expected)
    
    def test_address_to_dict(self):
        """Test converting Address to dictionary"""
        address = Address(
            street="789 Pine Rd",
            city="New York",
            state="NY",
            zip_code="10001"
        )
        
        dict_repr = address.to_dict()
        
        self.assertEqual(dict_repr['street'], "789 Pine Rd")
        self.assertEqual(dict_repr['city'], "New York")
        self.assertEqual(dict_repr['state'], "NY")
        self.assertEqual(dict_repr['zip_code'], "10001")
        self.assertEqual(dict_repr['country'], "USA")
    
    def test_address_from_dict(self):
        """Test creating Address from dictionary"""
        data = {
            'street': '321 Elm St',
            'city': 'Boston',
            'state': 'MA',
            'zip_code': '02108'
        }
        
        address = Address.from_dict(data)
        
        self.assertEqual(address.street, "321 Elm St")
        self.assertEqual(address.city, "Boston")
        self.assertEqual(address.state, "MA")
        self.assertEqual(address.zip_code, "02108")

# ==================== TEST ENUMS ====================

class TestProductCategory(unittest.TestCase):
    """Test ProductCategory enum"""
    
    def test_category_values(self):
        """Test category values"""
        self.assertEqual(ProductCategory.ELECTRONICS.value, "Electronics")
        self.assertEqual(ProductCategory.CLOTHING.value, "Clothing")
        self.assertEqual(ProductCategory.FOOD.value, "Food")
        self.assertEqual(ProductCategory.BOOKS.value, "Books")
    
    def test_all_categories(self):
        """Test getting all categories"""
        categories = ProductCategory.all_categories()
        
        self.assertIn("Electronics", categories)
        self.assertIn("Clothing", categories)
        self.assertIn("Food", categories)
        self.assertIn("Books", categories)
        self.assertEqual(len(categories), len(ProductCategory))

class TestOrderStatus(unittest.TestCase):
    """Test OrderStatus enum"""
    
    def test_status_transitions(self):
        """Test valid status transitions"""
        # Valid transitions
        self.assertTrue(OrderStatus.can_transition(
            OrderStatus.DRAFT, OrderStatus.PENDING
        ))
        self.assertTrue(OrderStatus.can_transition(
            OrderStatus.PENDING, OrderStatus.CONFIRMED
        ))
        self.assertTrue(OrderStatus.can_transition(
            OrderStatus.CONFIRMED, OrderStatus.PROCESSING
        ))
        
        # Invalid transitions
        self.assertFalse(OrderStatus.can_transition(
            OrderStatus.DELIVERED, OrderStatus.PROCESSING
        ))
        self.assertFalse(OrderStatus.can_transition(
            OrderStatus.CANCELLED, OrderStatus.PENDING
        ))
    
    def test_terminal_statuses(self):
        """Test terminal status detection"""
        self.assertTrue(OrderStatus.is_terminal_status(OrderStatus.DELIVERED))
        self.assertTrue(OrderStatus.is_terminal_status(OrderStatus.CANCELLED))
        self.assertTrue(OrderStatus.is_terminal_status(OrderStatus.REFUNDED))
        
        self.assertFalse(OrderStatus.is_terminal_status(OrderStatus.DRAFT))
        self.assertFalse(OrderStatus.is_terminal_status(OrderStatus.PENDING))
        self.assertFalse(OrderStatus.is_terminal_status(OrderStatus.PROCESSING))

class TestEmployeeRole(unittest.TestCase):
    """Test EmployeeRole enum"""
    
    def test_role_permissions(self):
        """Test role permissions"""
        # Manager should have extensive permissions
        manager_perms = EmployeeRole.MANAGER.get_permissions()
        self.assertIn("view_all", manager_perms)
        self.assertIn("edit_all", manager_perms)
        self.assertIn("manage_employees", manager_perms)
        
        # Warehouse worker should have limited permissions
        worker_perms = EmployeeRole.WAREHOUSE_WORKER.get_permissions()
        self.assertIn("view_products", worker_perms)
        self.assertIn("manage_inventory", worker_perms)
        self.assertNotIn("manage_employees", worker_perms)
    
    def test_has_permission(self):
        """Test permission checking"""
        self.assertTrue(EmployeeRole.MANAGER.has_permission("view_all"))
        self.assertTrue(EmployeeRole.MANAGER.has_permission("edit_all"))
        
        self.assertTrue(EmployeeRole.WAREHOUSE_WORKER.has_permission("view_products"))
        self.assertFalse(EmployeeRole.WAREHOUSE_WORKER.has_permission("edit_all"))

# ==================== TEST PRODUCT ENTITY ====================

class TestProductEntity(unittest.TestCase):
    """Test Product domain entity"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.product = Product(
            id="TEST-001",
            name="Test Product",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('100')),
            selling_price=Money(Decimal('150')),
            quantity=50,
            description="A test product",
            weight=Decimal('2.5')
        )
    
    def test_product_creation(self):
        """Test product creation with valid data"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.category, ProductCategory.ELECTRONICS)
        self.assertEqual(self.product.quantity, 50)
        self.assertEqual(self.product.purchase_price.amount, Decimal('100'))
        self.assertEqual(self.product.selling_price.amount, Decimal('150'))
        self.assertEqual(self.product.description, "A test product")
        self.assertEqual(self.product.weight, Decimal('2.5'))
        self.assertTrue(self.product.sku.startswith("ELE-"))
    
    def test_product_validation(self):
        """Test product validation rules"""
        # Test invalid name
        with self.assertRaises(ValueError):
            Product(
                id="TEST-002",
                name="A",  # Too short
                category=ProductCategory.ELECTRONICS,
                purchase_price=Money(Decimal('100')),
                selling_price=Money(Decimal('150')),
                quantity=10
            )
        
        # Test negative quantity
        with self.assertRaises(ValueError):
            Product(
                id="TEST-003",
                name="Valid Name",
                category=ProductCategory.ELECTRONICS,
                purchase_price=Money(Decimal('100')),
                selling_price=Money(Decimal('150')),
                quantity=-5  # Negative
            )
        
        # Test zero selling price
        with self.assertRaises(ValueError):
            Product(
                id="TEST-004",
                name="Valid Name",
                category=ProductCategory.ELECTRONICS,
                purchase_price=Money(Decimal('100')),
                selling_price=Money(Decimal('0')),  # Zero
                quantity=10
            )
        
        # Test selling price less than purchase price
        with self.assertRaises(ValueError):
            Product(
                id="TEST-005",
                name="Valid Name",
                category=ProductCategory.ELECTRONICS,
                purchase_price=Money(Decimal('100')),
                selling_price=Money(Decimal('80')),  # Less than purchase
                quantity=10
            )
    
    def test_quantity_operations(self):
        """Test quantity increase and decrease"""
        # Test increase
        initial_qty = self.product.quantity
        self.product.increase_quantity(20)
        self.assertEqual(self.product.quantity, initial_qty + 20)
        
        # Test decrease
        self.product.decrease_quantity(10)
        self.assertEqual(self.product.quantity, initial_qty + 10)
        
        # Test invalid increase (negative)
        with self.assertRaises(ValueError):
            self.product.increase_quantity(-5)
        
        # Test invalid decrease (negative)
        with self.assertRaises(ValueError):
            self.product.decrease_quantity(-5)
        
        # Test insufficient stock
        with self.assertRaises(ValueError):
            self.product.decrease_quantity(1000)  # More than available
    
    def test_max_stock_level(self):
        """Test max stock level constraint"""
        product = Product(
            id="TEST-MAX",
            name="Test Max",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('50')),
            selling_price=Money(Decimal('75')),
            quantity=900  # Close to max
        )
        
        # Should be able to add up to max
        product.increase_quantity(100)  # Now 1000
        
        # Should fail when exceeding max
        with self.assertRaises(ValueError):
            product.increase_quantity(1)
    
    def test_stock_status(self):
        """Test stock status detection"""
        # Create product with low stock
        low_stock_product = Product(
            id="TEST-LOW",
            name="Low Stock",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('50')),
            selling_price=Money(Decimal('75')),
            quantity=5  # Below MIN_STOCK_LEVEL
        )
        
        self.assertTrue(low_stock_product.is_low_stock())
        self.assertEqual(low_stock_product.get_stock_status(), "LOW STOCK")
        
        # Create product with warning stock
        warning_product = Product(
            id="TEST-WARN",
            name="Warning Stock",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('50')),
            selling_price=Money(Decimal('75')),
            quantity=30  # Between MIN and WARNING
        )
        
        self.assertFalse(warning_product.is_low_stock())
        self.assertTrue(warning_product.is_warning_stock())
        self.assertEqual(warning_product.get_stock_status(), "WARNING")
        
        # Create product with normal stock
        normal_product = Product(
            id="TEST-NORM",
            name="Normal Stock",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('50')),
            selling_price=Money(Decimal('75')),
            quantity=100  # Above WARNING
        )
        
        self.assertFalse(normal_product.is_low_stock())
        self.assertFalse(normal_product.is_warning_stock())
        self.assertEqual(normal_product.get_stock_status(), "IN STOCK")
    
    def test_profit_calculation(self):
        """Test profit margin calculation"""
        # Product with $100 purchase, $150 selling = 50% profit margin
        product = Product(
            id="TEST-PROFIT",
            name="Profit Test",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('100')),
            selling_price=Money(Decimal('150')),
            quantity=10
        )
        
        profit_margin = product.calculate_profit_margin()
        self.assertAlmostEqual(float(profit_margin), 50.0)
        
        # Test with small purchase price instead of zero
        small_price_product = Product(
            id="TEST-SMALL-PRICE",
            name="Low Cost Product",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('0.01')),  # Small but positive
            selling_price=Money(Decimal('100')),
            quantity=10
        )
        
        # Profit margin should be calculated
        self.assertGreater(small_price_product.calculate_profit_margin(), Decimal('0'))
    
    def test_total_value_calculation(self):
        """Test total inventory value calculation"""
        product = Product(
            id="TEST-VALUE",
            name="Value Test",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('50')),
            selling_price=Money(Decimal('75')),
            quantity=20
        )
        
        total_value = product.calculate_total_value()
        expected_value = Money(Decimal('1000'))  # 50 * 20
        
        self.assertEqual(total_value.amount, expected_value.amount)
    
    def test_order_fulfillment(self):
        """Test order fulfillment capability"""
        product = Product(
            id="TEST-FULFILL",
            name="Fulfill Test",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('50')),
            selling_price=Money(Decimal('75')),
            quantity=25
        )
        
        # Can fulfill order for 10 units
        self.assertTrue(product.can_fulfill_order(10))
        
        # Can fulfill order for exactly 25 units
        self.assertTrue(product.can_fulfill_order(25))
        
        # Cannot fulfill order for 30 units
        self.assertFalse(product.can_fulfill_order(30))
    
    def test_product_details(self):
        """Test product details dictionary"""
        details = self.product.get_details()
        
        # Check required fields
        self.assertIn('id', details)
        self.assertIn('name', details)
        self.assertIn('category', details)
        self.assertIn('quantity', details)
        self.assertIn('selling_price', details)
        self.assertIn('total_value', details)
        self.assertIn('profit_margin', details)
        self.assertIn('stock_status', details)
        
        # Check specific values
        self.assertEqual(details['name'], "Test Product")
        self.assertEqual(details['category'], "Electronics")
        self.assertEqual(details['quantity'], 50)
        self.assertIn("USD 150.00", details['selling_price'])
    
    def test_product_string_representation(self):
        """Test string representation of product"""
        product_str = str(self.product)
        
        self.assertIn("Test Product", product_str)
        self.assertIn("Electronics", product_str)
        self.assertIn("50", product_str)
        self.assertIn("USD 150.00", product_str)
    
    def test_product_equality(self):
        """Test product equality based on ID"""
        product1 = Product(
            id="SAME-ID",
            name="Product 1",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('100')),
            selling_price=Money(Decimal('150')),
            quantity=10
        )
        
        product2 = Product(
            id="SAME-ID",  # Same ID
            name="Product 2",  # Different name
            category=ProductCategory.CLOTHING,  # Different category
            purchase_price=Money(Decimal('50')),  # Different price
            selling_price=Money(Decimal('75')),  # Different price
            quantity=20  # Different quantity
        )
        
        product3 = Product(
            id="DIFFERENT-ID",  # Different ID
            name="Product 1",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('100')),
            selling_price=Money(Decimal('150')),
            quantity=10
        )
        
        self.assertEqual(product1, product2)  # Same ID
        self.assertNotEqual(product1, product3)  # Different ID

# ==================== TEST SPECIALIZED PRODUCTS ====================

class TestClothingProduct(unittest.TestCase):
    """Test ClothingProduct specialized entity"""
    
    def test_clothing_creation(self):
        """Test creating clothing product"""
        clothing = ClothingProduct(
            id="CLOTH-001",
            name="T-Shirt",
            category=ProductCategory.CLOTHING,
            purchase_price=Money(Decimal('10')),
            selling_price=Money(Decimal('25')),
            quantity=100,
            size="M",
            color="Blue",
            material="Cotton"
        )
        
        self.assertEqual(clothing.size, "M")
        self.assertEqual(clothing.color, "Blue")
        self.assertEqual(clothing.material, "Cotton")
        self.assertEqual(clothing.category, ProductCategory.CLOTHING)
    
    def test_clothing_details(self):
        """Test clothing product details"""
        clothing = ClothingProduct(
            id="CLOTH-002",
            name="Jeans",
            category=ProductCategory.CLOTHING,
            purchase_price=Money(Decimal('30')),
            selling_price=Money(Decimal('60')),
            quantity=50,
            size="32",
            color="Black",
            material="Denim"
        )
        
        details = clothing.get_details()
        
        self.assertEqual(details['size'], "32")
        self.assertEqual(details['color'], "Black")
        self.assertEqual(details['material'], "Denim")
        self.assertEqual(details['product_type'], 'Clothing')

class TestFoodProduct(unittest.TestCase):
    """Test FoodProduct specialized entity"""
    
    def test_food_creation(self):
        """Test creating food product"""
        expiration_date = date.today() + timedelta(days=30)
        food = FoodProduct(
            id="FOOD-001",
            name="Chocolate",
            category=ProductCategory.FOOD,
            purchase_price=Money(Decimal('2')),
            selling_price=Money(Decimal('5')),
            quantity=200,
            expiration_date=expiration_date,
            storage_temperature=Decimal('4')  # Celsius
        )
        
        self.assertEqual(food.expiration_date, expiration_date)
        self.assertEqual(food.storage_temperature, Decimal('4'))
        self.assertEqual(food.category, ProductCategory.FOOD)
    
    def test_food_expiration(self):
        """Test food expiration logic"""
        # Product expiring tomorrow
        tomorrow = date.today() + timedelta(days=1)
        fresh_food = FoodProduct(
            id="FOOD-FRESH",
            name="Milk",
            category=ProductCategory.FOOD,
            purchase_price=Money(Decimal('3')),
            selling_price=Money(Decimal('6')),
            quantity=20,
            expiration_date=tomorrow
        )
        
        self.assertFalse(fresh_food.is_expired())
        self.assertEqual(fresh_food.days_until_expiration(), 1)
        
        # Product expired yesterday
        yesterday = date.today() - timedelta(days=1)
        expired_food = FoodProduct(
            id="FOOD-EXPIRED",
            name="Bread",
            category=ProductCategory.FOOD,
            purchase_price=Money(Decimal('1')),
            selling_price=Money(Decimal('2')),
            quantity=5,
            expiration_date=yesterday
        )
        
        self.assertTrue(expired_food.is_expired())
        self.assertEqual(expired_food.days_until_expiration(), 0)
        
        # Product without expiration date
        no_expiry_food = FoodProduct(
            id="FOOD-NO-EXPIRY",
            name="Canned Beans",
            category=ProductCategory.FOOD,
            purchase_price=Money(Decimal('2')),
            selling_price=Money(Decimal('4')),
            quantity=30
        )
        
        self.assertFalse(no_expiry_food.is_expired())
        self.assertIsNone(no_expiry_food.days_until_expiration())
    
    def test_food_details(self):
        """Test food product details"""
        expiration_date = date.today() + timedelta(days=60)
        food = FoodProduct(
            id="FOOD-003",
            name="Cheese",
            category=ProductCategory.FOOD,
            purchase_price=Money(Decimal('5')),
            selling_price=Money(Decimal('10')),
            quantity=15,
            expiration_date=expiration_date
        )
        
        details = food.get_details()
        
        self.assertEqual(details['expiration_date'], expiration_date.isoformat())
        self.assertFalse(details['is_expired'])
        self.assertEqual(details['days_until_expiration'], 60)
        self.assertEqual(details['product_type'], 'Food')

class TestBookProduct(unittest.TestCase):
    """Test BookProduct specialized entity"""
    
    def test_book_creation(self):
        """Test creating book product"""
        book = BookProduct(
            id="BOOK-001",
            name="Python Programming",
            category=ProductCategory.BOOKS,
            purchase_price=Money(Decimal('20')),
            selling_price=Money(Decimal('35')),
            quantity=50,
            author="John Doe",
            isbn="978-3-16-148410-0",
            publisher="Tech Books",
            publication_year=2023
        )
        
        self.assertEqual(book.author, "John Doe")
        self.assertEqual(book.isbn, "978-3-16-148410-0")
        self.assertEqual(book.publisher, "Tech Books")
        self.assertEqual(book.publication_year, 2023)
        self.assertEqual(book.category, ProductCategory.BOOKS)
    
    def test_book_details(self):
        """Test book product details"""
        book = BookProduct(
            id="BOOK-002",
            name="Clean Code",
            category=ProductCategory.BOOKS,
            purchase_price=Money(Decimal('25')),
            selling_price=Money(Decimal('45')),
            quantity=30,
            author="Robert Martin",
            isbn="978-0-13-235088-4"
        )
        
        details = book.get_details()
        
        self.assertEqual(details['author'], "Robert Martin")
        self.assertEqual(details['isbn'], "978-0-13-235088-4")
        self.assertEqual(details['product_type'], 'Book')

# ==================== TEST ORDER ENTITY ====================

class TestOrderEntity(unittest.TestCase):
    """Test Order domain entity"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.address = Address(
            street="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62704"
        )
        
        self.product1 = Product(
            id="PROD-001",
            name="Laptop",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('800')),
            selling_price=Money(Decimal('1200')),
            quantity=10
        )
        
        self.product2 = Product(
            id="PROD-002",
            name="Mouse",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('20')),
            selling_price=Money(Decimal('35')),
            quantity=50
        )
        
        self.order = Order(
            id="ORD-001",
            customer_name="John Doe",
            customer_email="john@example.com",
            shipping_address=self.address,
            billing_address=self.address
        )
    
    def test_order_creation(self):
        """Test order creation"""
        self.assertEqual(self.order.customer_name, "John Doe")
        self.assertEqual(self.order.customer_email, "john@example.com")
        self.assertEqual(self.order.shipping_address, self.address)
        self.assertEqual(self.order.billing_address, self.address)
        self.assertEqual(self.order.status, OrderStatus.DRAFT)
        self.assertEqual(self.order.get_item_count(), 0)
    
    def test_order_validation(self):
        """Test order validation rules"""
        # Invalid customer name
        with self.assertRaises(ValueError):
            Order(
                id="ORD-INVALID",
                customer_name="A",  # Too short
                customer_email="test@example.com"
            )
        
        # Invalid email
        with self.assertRaises(ValueError):
            Order(
                id="ORD-INVALID-EMAIL",
                customer_name="Valid Name",
                customer_email="invalid-email"  # No @
            )
    
    def test_add_items_to_order(self):
        """Test adding items to order"""
        # Add first product
        self.order.add_item(self.product1, 2)
        self.assertEqual(self.order.get_item_count(), 2)
        
        # Add second product
        self.order.add_item(self.product2, 3)
        self.assertEqual(self.order.get_item_count(), 5)
        
        # Add more of first product
        self.order.add_item(self.product1, 1)
        self.assertEqual(self.order.get_item_count(), 6)
        
        # Verify items list
        items = self.order.get_items()
        self.assertEqual(len(items), 2)  # Two different products
        
        # Check quantities
        for item in items:
            if item.product_id == "PROD-001":
                self.assertEqual(item.quantity, 3)
            elif item.product_id == "PROD-002":
                self.assertEqual(item.quantity, 3)
    
    def test_add_item_insufficient_stock(self):
        """Test adding item with insufficient stock"""
        # Product only has 10 units
        with self.assertRaises(ValueError):
            self.order.add_item(self.product1, 15)  # Requesting 15
    
    def test_remove_items_from_order(self):
        """Test removing items from order"""
        # Add items first
        self.order.add_item(self.product1, 2)
        self.order.add_item(self.product2, 3)
        
        # Remove first product
        result = self.order.remove_item("PROD-001")
        self.assertTrue(result)
        self.assertEqual(self.order.get_item_count(), 3)  # Only mouse left
        
        # Remove non-existent product
        result = self.order.remove_item("NON-EXISTENT")
        self.assertFalse(result)
        self.assertEqual(self.order.get_item_count(), 3)
    
    def test_update_item_quantity(self):
        """Test updating item quantity"""
        # Add item first
        self.order.add_item(self.product1, 2)
        
        # Update quantity
        result = self.order.update_item_quantity("PROD-001", 5)
        self.assertTrue(result)
        self.assertEqual(self.order.get_item_count(), 5)
        
        # Update to zero (should remove)
        result = self.order.update_item_quantity("PROD-001", 0)
        self.assertTrue(result)
        self.assertEqual(self.order.get_item_count(), 0)
        
        # Update non-existent item
        result = self.order.update_item_quantity("NON-EXISTENT", 5)
        self.assertFalse(result)
    
    def test_order_calculations(self):
        """Test order calculations"""
        # Add items
        self.order.add_item(self.product1, 2)  # 2 * $1200 = $2400
        self.order.add_item(self.product2, 4)  # 4 * $35 = $140
        
        # Test subtotal
        subtotal = self.order.calculate_subtotal()
        self.assertEqual(subtotal.amount, Decimal('2540'))  # 2400 + 140
        
        # Test tax calculation (10% default)
        tax = self.order.calculate_tax()
        self.assertEqual(tax.amount, Decimal('254'))  # 2540 * 0.1
        
        # Test shipping cost (base $10 + $1 per item)
        shipping = self.order.calculate_shipping_cost()
        self.assertEqual(shipping.amount, Decimal('16'))  # 10 + (6 items * 1)
        
        # Test discount calculation
        discount = self.order.calculate_discount(Decimal('10'))  # 10% discount
        self.assertEqual(discount.amount, Decimal('254'))  # 2540 * 0.1
        
        # Test total calculation
        total = self.order.calculate_total()
        expected = Decimal('2540') + Decimal('254') + Decimal('16')  # subtotal + tax + shipping
        self.assertEqual(total.amount, expected)
        
        # Test total with discount
        total_with_discount = self.order.calculate_total(discount_percentage=Decimal('10'))
        expected_with_discount = Decimal('2540') + Decimal('254') + Decimal('16') - Decimal('254')
        self.assertEqual(total_with_discount.amount, expected_with_discount)
    
    def test_order_status_transitions(self):
        """Test order status transitions"""
        # Start with DRAFT
        self.assertEqual(self.order.status, OrderStatus.DRAFT)
        
        # Valid transitions
        self.order.change_status(OrderStatus.PENDING)
        self.assertEqual(self.order.status, OrderStatus.PENDING)
        
        self.order.change_status(OrderStatus.CONFIRMED)
        self.assertEqual(self.order.status, OrderStatus.CONFIRMED)
        
        self.order.change_status(OrderStatus.PROCESSING)
        self.assertEqual(self.order.status, OrderStatus.PROCESSING)
        
        self.order.change_status(OrderStatus.SHIPPED)
        self.assertEqual(self.order.status, OrderStatus.SHIPPED)
        
        self.order.change_status(OrderStatus.DELIVERED)
        self.assertEqual(self.order.status, OrderStatus.DELIVERED)
        
        # Invalid transition (cannot go back)
        with self.assertRaises(ValueError):
            self.order.change_status(OrderStatus.PROCESSING)
    
    def test_cancellation_rules(self):
        """Test order cancellation rules"""
        # Fresh order can be cancelled
        fresh_order = Order(
            id="ORD-CANCEL",
            customer_name="Test",
            customer_email="test@example.com"
        )
        
        self.assertTrue(fresh_order.can_be_cancelled())
        
        # Order in terminal status cannot be cancelled
        delivered_order = Order(
            id="ORD-DELIVERED",
            customer_name="Test",
            customer_email="test@example.com"
        )
        delivered_order._status = OrderStatus.DELIVERED
        
        self.assertFalse(delivered_order.can_be_cancelled())
        
        # Cancelled order cannot be cancelled again
        cancelled_order = Order(
            id="ORD-CANCELLED",
            customer_name="Test",
            customer_email="test@example.com"
        )
        cancelled_order._status = OrderStatus.CANCELLED
        
        self.assertFalse(cancelled_order.can_be_cancelled())
    
    def test_modification_rules(self):
        """Test order modification rules"""
        # Draft order can be modified
        draft_order = Order(
            id="ORD-DRAFT",
            customer_name="Test",
            customer_email="test@example.com"
        )
        
        self.assertTrue(draft_order.can_be_modified())
        
        # Pending order can be modified
        pending_order = Order(
            id="ORD-PENDING",
            customer_name="Test",
            customer_email="test@example.com"
        )
        pending_order._status = OrderStatus.PENDING
        
        self.assertTrue(pending_order.can_be_modified())
        
        # Processing order cannot be modified
        processing_order = Order(
            id="ORD-PROCESSING",
            customer_name="Test",
            customer_email="test@example.com"
        )
        processing_order._status = OrderStatus.PROCESSING
        
        self.assertFalse(processing_order.can_be_modified())
    
    def test_completion_status(self):
        """Test order completion status"""
        # Delivered order is completed
        delivered_order = Order(
            id="ORD-DELIVERED",
            customer_name="Test",
            customer_email="test@example.com"
        )
        delivered_order._status = OrderStatus.DELIVERED
        
        self.assertTrue(delivered_order.is_completed())
        
        # Refunded order is completed
        refunded_order = Order(
            id="ORD-REFUNDED",
            customer_name="Test",
            customer_email="test@example.com"
        )
        refunded_order._status = OrderStatus.REFUNDED
        
        self.assertTrue(refunded_order.is_completed())
        
        # Processing order is not completed
        processing_order = Order(
            id="ORD-PROCESSING",
            customer_name="Test",
            customer_email="test@example.com"
        )
        processing_order._status = OrderStatus.PROCESSING
        
        self.assertFalse(processing_order.is_completed())
    
    def test_order_summary(self):
        """Test order summary generation"""
        # Add items
        self.order.add_item(self.product1, 1)
        self.order.add_item(self.product2, 2)
        
        # Get summary
        summary = self.order.get_summary()
        
        # Check required fields
        self.assertIn('id', summary)
        self.assertIn('customer_name', summary)
        self.assertIn('customer_email', summary)
        self.assertIn('status', summary)
        self.assertIn('item_count', summary)
        self.assertIn('subtotal', summary)
        self.assertIn('total', summary)
        self.assertIn('created_at', summary)
        self.assertIn('updated_at', summary)
        
        # Check values
        self.assertEqual(summary['customer_name'], "John Doe")
        self.assertEqual(summary['customer_email'], "john@example.com")
        self.assertEqual(summary['status'], "Draft")
        self.assertEqual(summary['item_count'], 3)
    
    def test_detailed_summary(self):
        """Test detailed order summary"""
        # Add items
        self.order.add_item(self.product1, 1)
        
        # Get detailed summary
        details = self.order.get_detailed_summary()
        
        # Should include items list
        self.assertIn('items', details)
        self.assertIn('item_details', details)
        
        self.assertEqual(len(details['items']), 1)
        self.assertEqual(len(details['item_details']), 1)
        
        # Check item details
        item_detail = details['item_details'][0]
        self.assertIn("Laptop", item_detail)
        self.assertIn("x1", item_detail)

# ==================== TEST EMPLOYEE ENTITY ====================

class TestEmployeeEntity(unittest.TestCase):
    """Test Employee domain entity"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.employee = Employee(
            id="EMP-001",
            name="John Doe",
            email="john.doe@company.com",
            role=EmployeeRole.MANAGER,
            salary=Money(Decimal('50000')),  # Fixed: from 5000 to 50000
            department="Management",
            phone="+1-234-567-8900",
            hire_date=date(2020, 1, 15)
        )
    
    def test_employee_creation(self):
        """Test employee creation"""
        self.assertEqual(self.employee.name, "John Doe")
        self.assertEqual(self.employee.email, "john.doe@company.com")
        self.assertEqual(self.employee.role, EmployeeRole.MANAGER)
        self.assertEqual(self.employee.salary.amount, Decimal('50000'))
        self.assertEqual(self.employee.department, "Management")
        self.assertEqual(self.employee.phone, "+1-234-567-8900")
        self.assertEqual(self.employee.hire_date, date(2020, 1, 15))
        self.assertEqual(self.employee.performance_rating, Decimal('0'))
    
    def test_employee_validation(self):
        """Test employee validation rules"""
        # Invalid name
        with self.assertRaises(ValueError):
            Employee(
                id="EMP-INVALID",
                name="A",  # Too short
                email="valid@email.com",
                role=EmployeeRole.MANAGER,
                salary=Money(Decimal('50000'))
            )
        
        # Invalid email
        with self.assertRaises(ValueError):
            Employee(
                id="EMP-INVALID-EMAIL",
                name="Valid Name",
                email="invalid-email",  # No @
                role=EmployeeRole.MANAGER,
                salary=Money(Decimal('50000'))
            )
        
        # Salary below minimum
        with self.assertRaises(ValueError):
            Employee(
                id="EMP-LOW-SALARY",
                name="Valid Name",
                email="valid@email.com",
                role=EmployeeRole.MANAGER,
                salary=Money(Decimal('5000'))  # Below MIN_SALARY
            )
        
        # Salary above maximum (adjusted for test)
        with self.assertRaises(ValueError):
            Employee(
                id="EMP-HIGH-SALARY",
                name="Valid Name",
                email="valid@email.com",
                role=EmployeeRole.MANAGER,
                salary=Money(Decimal('2000000'))  # Above MAX_SALARY
            )
    
    def test_years_of_service(self):
        """Test years of service calculation"""
        # Hire date 3 years ago
        hire_date = date.today().replace(year=date.today().year - 3)
        employee = Employee(
            id="EMP-YOS",
            name="Test",
            email="test@company.com",
            role=EmployeeRole.MANAGER,
            salary=Money(Decimal('50000')),
            hire_date=hire_date
        )
        
        years = employee.calculate_years_of_service()
        self.assertEqual(years, 3)
        
        # Hire date today
        today_employee = Employee(
            id="EMP-TODAY",
            name="Test",
            email="test@company.com",
            role=EmployeeRole.MANAGER,
            salary=Money(Decimal('50000')),
            hire_date=date.today()
        )
        
        self.assertEqual(today_employee.calculate_years_of_service(), 0)
    
    def test_task_management(self):
        """Test task assignment and removal"""
        # Initially no tasks
        self.assertEqual(len(self.employee.get_tasks()), 0)
        
        # Assign tasks
        self.employee.assign_task("Complete report")
        self.employee.assign_task("Attend meeting")
        
        tasks = self.employee.get_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertIn("Complete report", tasks)
        self.assertIn("Attend meeting", tasks)
        
        # Remove task
        result = self.employee.remove_task("Complete report")
        self.assertTrue(result)
        self.assertEqual(len(self.employee.get_tasks()), 1)
        self.assertIn("Attend meeting", self.employee.get_tasks())
        
        # Remove non-existent task
        result = self.employee.remove_task("Non-existent task")
        self.assertFalse(result)
        self.assertEqual(len(self.employee.get_tasks()), 1)
        
        # Assign duplicate task (should not duplicate)
        self.employee.assign_task("Attend meeting")
        self.assertEqual(len(self.employee.get_tasks()), 1)
    
        def test_permission_checking(self):
         """Test permission checking"""
        # Manager should have manager permissions
        self.assertTrue(self.employee.has_permission("manage_employees"))
        self.assertTrue(self.employee.has_permission("view_all"))
        self.assertTrue(self.employee.has_permission("edit_all"))
        
        # Manager should not have non-existent permission
        self.assertFalse(self.employee.has_permission("non_existent_permission"))
        
        # Create warehouse worker
        worker = Employee(
            id="EMP-WORKER",
            name="Worker",
            email="worker@company.com",
            role=EmployeeRole.WAREHOUSE_WORKER,
            salary=Money(Decimal('30000'))
        )
        
        # Worker should have worker permissions
        self.assertTrue(worker.has_permission("view_products"))
        self.assertTrue(worker.has_permission("manage_inventory"))
        
        # Worker should not have manager permissions
        self.assertFalse(worker.has_permission("manage_employees"))

    def test_management_capability(self):  # <-- هنا يجب أن تكون في نفس مستوى test_permission_checking
        """Test management capability checking"""
        # Create employees with different roles
        manager = Employee(
            id="EMP-MGR",
            name="Manager",
            email="manager@company.com",
            role=EmployeeRole.MANAGER,
            salary=Money(Decimal('60000'))
        )
        
        supervisor = Employee(
            id="EMP-SUP",
            name="Supervisor",
            email="supervisor@company.com",
            role=EmployeeRole.SUPERVISOR,
            salary=Money(Decimal('45000'))
        )
        
        worker = Employee(
            id="EMP-WRK",
            name="Worker",
            email="worker@company.com",
            role=EmployeeRole.WAREHOUSE_WORKER,
            salary=Money(Decimal('30000'))
        )
        
        accountant = Employee(
            id="EMP-ACC",
            name="Accountant",
            email="accountant@company.com",
            role=EmployeeRole.ACCOUNTANT,
            salary=Money(Decimal('40000'))
        )
        
        # Test manager capabilities
        self.assertTrue(manager.can_manage(supervisor))    # Manager can manage supervisor
        self.assertTrue(manager.can_manage(worker))        # Manager can manage worker
        self.assertFalse(manager.can_manage(accountant))   # Manager cannot manage accountant
        
        # Test supervisor capabilities  
        self.assertFalse(supervisor.can_manage(manager))   # Supervisor cannot manage manager
        self.assertTrue(supervisor.can_manage(worker))     # Supervisor can manage worker
        self.assertFalse(supervisor.can_manage(accountant)) # Supervisor cannot manage accountant
        
        # Test worker capabilities
        self.assertFalse(worker.can_manage(manager))       # Worker cannot manage manager
        self.assertFalse(worker.can_manage(supervisor))    # Worker cannot manage supervisor
        self.assertFalse(worker.can_manage(accountant))    # Worker cannot manage accountant

    def test_bonus_calculation(self):
        """Test bonus calculation"""
        employee = Employee(
            id="EMP-BONUS",
            name="Bonus Test",
            email="bonus@company.com",
            role=EmployeeRole.MANAGER,
            salary=Money(Decimal('50000'))
        )
        # Set performance rating separately
        employee.performance_rating = Decimal('4.5')  # Excellent
        
        # Calculate 10% bonus
        bonus = employee.calculate_bonus(Decimal('0.1'))
        
        # Base bonus: 50000 * 0.1 = 5000
        # Performance multiplier: 1 + (4.5/10) = 1.45
        # Total: 5000 * 1.45 = 7250
        expected_bonus = Decimal('50000') * Decimal('0.1') * (Decimal('1') + Decimal('4.5')/Decimal('10'))
        self.assertEqual(bonus.amount, expected_bonus)
        
        # Test with invalid bonus percentage
        with self.assertRaises(ValueError):
            employee.calculate_bonus(Decimal('1.5'))  # > 100%
        
        with self.assertRaises(ValueError):
            employee.calculate_bonus(Decimal('-0.1'))  # Negative
    
    def test_employee_info(self):
        """Test employee information generation"""
        info = self.employee.get_info()
        
        # Check required fields
        self.assertIn('id', info)
        self.assertIn('name', info)
        self.assertIn('email', info)
        self.assertIn('role', info)
        self.assertIn('salary', info)
        self.assertIn('hire_date', info)
        self.assertIn('years_of_service', info)
        self.assertIn('task_count', info)
        self.assertIn('performance_rating', info)
        self.assertIn('permissions', info)
        self.assertIn('created_at', info)
        self.assertIn('updated_at', info)
        
        # Check specific values
        self.assertEqual(info['name'], "John Doe")
        self.assertEqual(info['email'], "john.doe@company.com")
        self.assertEqual(info['role'], "Manager")
        self.assertIn("USD 50000.00", info['salary'])
        self.assertEqual(info['hire_date'], "2020-01-15")
        self.assertEqual(info['task_count'], 0)
        self.assertEqual(info['performance_rating'], "0")

# ==================== TEST ORDER ITEM ====================

class TestOrderItem(unittest.TestCase):
    """Test OrderItem value object"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.order_item = OrderItem(
            product_id="PROD-001",
            product_name="Laptop",
            unit_price=Money(Decimal('1200')),
            quantity=2
        )
    
    def test_order_item_creation(self):
        """Test order item creation"""
        self.assertEqual(self.order_item.product_id, "PROD-001")
        self.assertEqual(self.order_item.product_name, "Laptop")
        self.assertEqual(self.order_item.unit_price.amount, Decimal('1200'))
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.total_price.amount, Decimal('2400'))
    
    def test_order_item_validation(self):
        """Test order item validation"""
        # Zero quantity
        with self.assertRaises(ValueError):
            OrderItem(
                product_id="PROD-001",
                product_name="Product",
                unit_price=Money(Decimal('100')),
                quantity=0
            )
        
        # Negative quantity
        with self.assertRaises(ValueError):
            OrderItem(
                product_id="PROD-001",
                product_name="Product",
                unit_price=Money(Decimal('100')),
                quantity=-5
            )
        
        # Zero price
        with self.assertRaises(ValueError):
            OrderItem(
                product_id="PROD-001",
                product_name="Product",
                unit_price=Money(Decimal('0')),
                quantity=5
            )
    
    def test_total_calculation(self):
        """Test total calculation"""
        total = self.order_item.calculate_total()
        self.assertEqual(total.amount, Decimal('2400'))  # 1200 * 2
        
        # Update quantity and verify total updates
        self.order_item.increase_quantity(1)
        self.assertEqual(self.order_item.quantity, 3)
        self.assertEqual(self.order_item.total_price.amount, Decimal('3600'))  # 1200 * 3
    
    def test_quantity_operations(self):
        """Test quantity operations"""
        # Increase quantity
        self.order_item.increase_quantity(3)
        self.assertEqual(self.order_item.quantity, 5)
        self.assertEqual(self.order_item.total_price.amount, Decimal('6000'))
        
        # Decrease quantity
        self.order_item.decrease_quantity(2)
        self.assertEqual(self.order_item.quantity, 3)
        self.assertEqual(self.order_item.total_price.amount, Decimal('3600'))
        
        # Invalid increase
        with self.assertRaises(ValueError):
            self.order_item.increase_quantity(0)
        
        with self.assertRaises(ValueError):
            self.order_item.increase_quantity(-1)
        
        # Invalid decrease
        with self.assertRaises(ValueError):
            self.order_item.decrease_quantity(0)
        
        with self.assertRaises(ValueError):
            self.order_item.decrease_quantity(-1)
        
        # Decrease below zero
        with self.assertRaises(ValueError):
            self.order_item.decrease_quantity(10)
    
    def test_price_update(self):
        """Test price update"""
        # Update price
        self.order_item.update_price(Money(Decimal('1300')))
        
        self.assertEqual(self.order_item.unit_price.amount, Decimal('1300'))
        self.assertEqual(self.order_item.total_price.amount, Decimal('2600'))  # 1300 * 2
        
        # Invalid price update
        with self.assertRaises(ValueError):
            self.order_item.update_price(Money(Decimal('0')))
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        dict_repr = self.order_item.to_dict()
        
        self.assertEqual(dict_repr['product_id'], "PROD-001")
        self.assertEqual(dict_repr['product_name'], "Laptop")
        self.assertEqual(dict_repr['unit_price'], "USD 1200.00")
        self.assertEqual(dict_repr['quantity'], 2)
        self.assertEqual(dict_repr['total_price'], "USD 2400.00")
    
    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            'product_id': 'PROD-002',
            'product_name': 'Mouse',
            'unit_price': 'USD 35.00',
            'quantity': 4
        }
        
        order_item = OrderItem.from_dict(data)
        
        self.assertEqual(order_item.product_id, "PROD-002")
        self.assertEqual(order_item.product_name, "Mouse")
        self.assertEqual(order_item.unit_price.amount, Decimal('35'))
        self.assertEqual(order_item.quantity, 4)
        self.assertEqual(order_item.total_price.amount, Decimal('140'))
    
    def test_string_representation(self):
        """Test string representation"""
        item_str = str(self.order_item)
        
        self.assertIn("Laptop", item_str)
        self.assertIn("x2", item_str)
        self.assertIn("USD 1200.00", item_str)
        self.assertIn("USD 2400.00", item_str)

# ==================== TEST DESIGN PATTERNS ====================

class TestStrategyPattern(unittest.TestCase):
    """Test Strategy Pattern implementations"""
    
    def test_regular_pricing(self):
        """Test regular pricing strategy"""
        strategy = RegularPricing()
        
        # Test calculation
        result = strategy.calculate_total(price=Decimal('100'), quantity=5)
        self.assertEqual(result, Decimal('500'))  # 100 * 5
        
        # Test description
        self.assertEqual(strategy.get_description(), "Regular Pricing (No Discount)")
    
    def test_bulk_discount_pricing(self):
        """Test bulk discount pricing strategy"""
        strategy = BulkDiscountPricing(
            discount_rate=Decimal('0.1'),  # 10% discount
            min_quantity=10
        )
        
        # Test below minimum quantity (no discount)
        result1 = strategy.calculate_total(price=Decimal('50'), quantity=5)
        self.assertEqual(result1, Decimal('250'))  # 50 * 5
        
        # Test at minimum quantity (with discount)
        result2 = strategy.calculate_total(price=Decimal('50'), quantity=10)
        expected2 = Decimal('50') * 10 * Decimal('0.9')  # 10% off
        self.assertEqual(result2, expected2)
        
        # Test above minimum quantity (with discount)
        result3 = strategy.calculate_total(price=Decimal('50'), quantity=20)
        expected3 = Decimal('50') * 20 * Decimal('0.9')  # 10% off
        self.assertEqual(result3, expected3)
        
        # Test description
        self.assertEqual(strategy.get_description(), "Bulk Discount (10.0% off for 10+ items)")
    
    def test_seasonal_pricing(self):
        """Test seasonal pricing strategy"""
        strategy = SeasonalPricing(seasonal_multiplier=Decimal('1.2'))  # 20% increase
        
        result = strategy.calculate_total(price=Decimal('100'), quantity=5)
        expected = Decimal('100') * 5 * Decimal('1.2')
        self.assertEqual(result, expected)
        
        # Test with discount (multiplier < 1)
        discount_strategy = SeasonalPricing(seasonal_multiplier=Decimal('0.8'))  # 20% discount
        discount_result = discount_strategy.calculate_total(price=Decimal('100'), quantity=5)
        discount_expected = Decimal('100') * 5 * Decimal('0.8')
        self.assertEqual(discount_result, discount_expected)
    
    def test_strategy_interchangeability(self):
        """Test that strategies are interchangeable"""
        price = Decimal('75')
        quantity = 8
        
        strategies = [
            RegularPricing(),
            BulkDiscountPricing(discount_rate=Decimal('0.15'), min_quantity=5),
            SeasonalPricing(seasonal_multiplier=Decimal('0.9'))
        ]
        
        results = []
        for strategy in strategies:
            result = strategy.calculate_total(price, quantity)
            results.append(result)
            # All should produce Decimal results
            self.assertIsInstance(result, Decimal)
            self.assertGreater(result, Decimal('0'))
        
        # Should have 3 different results
        self.assertEqual(len(results), 3)
        self.assertEqual(len(set(results)), 3)  # All should be different

class TestObserverPattern(unittest.TestCase):
    """Test Observer Pattern implementations"""
    
    def test_email_notifier(self):
        """Test email notifier"""
        notifier = EmailNotifier("test@example.com")
        
        # Test update method
        try:
            # Capture print output
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                notifier.update(
                    product_id="PROD-001",
                    product_name="Test Product",
                    quantity=5,
                    threshold=10
                )
            
            output = f.getvalue()
            
            # Check output contains expected information
            self.assertIn("EMAIL to test@example.com", output)
            self.assertIn("Test Product", output)
            self.assertIn("low on stock", output)
            self.assertIn("5", output)
            self.assertIn("10", output)
            
        except Exception as e:
            self.fail(f"EmailNotifier.update() failed: {e}")
        
        # Test observer type
        self.assertEqual(notifier.get_observer_type(), "Email Notifier")
        
        # Test notification count
        self.assertEqual(notifier.notification_count, 1)
    
    def test_log_notifier(self):
        """Test log notifier"""
        import tempfile
        import os
        
        # Create temporary log file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_file = f.name
        
        try:
            notifier = LogNotifier(log_file)
            
            # Test update method
            notifier.update(
                product_id="PROD-002",
                product_name="Another Product",
                quantity=3,
                threshold=15
            )
            
            # Check notification was recorded
            self.assertEqual(len(notifier.notifications), 1)
            
            notification = notifier.notifications[0]
            self.assertEqual(notification['product_id'], "PROD-002")
            self.assertEqual(notification['product_name'], "Another Product")
            self.assertEqual(notification['quantity'], 3)
            self.assertEqual(notification['threshold'], 15)
            self.assertIn("Low stock alert", notification['message'])
            
            # Check log file was created and has content
            self.assertTrue(os.path.exists(log_file))
            
            with open(log_file, 'r') as f:
                log_content = f.read()
                self.assertIn("Low stock alert", log_content)
                self.assertIn("Another Product", log_content)
            
            # Test observer type
            self.assertEqual(notifier.get_observer_type(), "Log Notifier")
            
        finally:
            # Clean up
            if os.path.exists(log_file):
                os.remove(log_file)
    
    def test_multiple_observers(self):
        """Test multiple observers on a product"""
        # Create product
        product = Product(
            id="OBS-TEST",
            name="Observer Test",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('100')),
            selling_price=Money(Decimal('150')),
            quantity=20
        )
        
        # Create observers
        class TestObserver(InventoryObserver):
            def __init__(self, name):
                self.name = name
                self.notifications = []
            
            def update(self, product_id, product_name, quantity, threshold):
                self.notifications.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'quantity': quantity,
                    'threshold': threshold
                })
            
            def get_observer_type(self):
                return f"Test Observer {self.name}"
        
        observer1 = TestObserver("A")
        observer2 = TestObserver("B")
        
        # Attach observers
        product.attach_observer(observer1)
        product.attach_observer(observer2)
        
        # Reduce stock to trigger notification
        product.decrease_quantity(15)  # Now 5 units (below threshold)
        
        # Both observers should have been notified
        self.assertEqual(len(observer1.notifications), 1)
        self.assertEqual(len(observer2.notifications), 1)
        
        # Check notification content
        for observer in [observer1, observer2]:
            notification = observer.notifications[0]
            self.assertEqual(notification['product_id'], "OBS-TEST")
            self.assertEqual(notification['product_name'], "Observer Test")
            self.assertEqual(notification['quantity'], 5)
            self.assertEqual(notification['threshold'], 10)  # MIN_STOCK_LEVEL
        
        # Detach observer
        product.detach_observer(observer1)
        
        # Trigger another notification
        product._notify_observers()
        
        # Only observer2 should get second notification
        self.assertEqual(len(observer1.notifications), 1)  # Still 1
        self.assertEqual(len(observer2.notifications), 2)  # Now 2

class TestFactoryPattern(unittest.TestCase):
    """Test Factory Pattern implementations"""
    
    def test_electronics_factory(self):
        """Test electronics product factory"""
        product = ProductFactory.create_electronics(
            name="Smartphone",
            purchase_price=Decimal('300'),
            selling_price=Decimal('500'),
            quantity=25
        )
        
        # Check product type and properties
        self.assertIsInstance(product, Product)
        self.assertEqual(product.name, "Smartphone")
        self.assertEqual(product.category, ProductCategory.ELECTRONICS)
        self.assertEqual(product.purchase_price.amount, Decimal('300'))
        self.assertEqual(product.selling_price.amount, Decimal('500'))
        self.assertEqual(product.quantity, 25)
        
        # Check ID format
        self.assertTrue(product.id.startswith("ELEC-"))
        self.assertEqual(len(product.id), 13)  # ELEC- + 8 chars
        
        # Check SKU format
        self.assertTrue(product.sku.startswith("ELE-"))
    
    def test_clothing_factory(self):
        """Test clothing product factory"""
        product = ProductFactory.create_clothing(
            name="Jacket",
            purchase_price=Decimal('40'),
            selling_price=Decimal('80'),
            quantity=60,
            size="L",
            color="Black"
            # Removed 'material' parameter
        )
        
        # Check product type
        self.assertIsInstance(product, ClothingProduct)
        self.assertEqual(product.name, "Jacket")
        self.assertEqual(product.category, ProductCategory.CLOTHING)
        
        # Check specialized properties
        self.assertEqual(product.size, "L")
        self.assertEqual(product.color, "Black")
        # Material will be default value
        
        # Check ID format
        self.assertTrue(product.id.startswith("CLOTH-"))
        
        # Check SKU format
        self.assertTrue(product.sku.startswith("CLO-"))
    
    def test_food_factory(self):
        """Test food product factory"""
        expiration_date = date.today() + timedelta(days=90)
        product = ProductFactory.create_food(
            name="Yogurt",
            purchase_price=Decimal('1'),
            selling_price=Decimal('3'),
            quantity=100,
            expiration_date=expiration_date
        )
        
        # Check product type
        self.assertIsInstance(product, FoodProduct)
        self.assertEqual(product.name, "Yogurt")
        self.assertEqual(product.category, ProductCategory.FOOD)
        
        # Check specialized properties
        self.assertEqual(product.expiration_date, expiration_date)
        self.assertFalse(product.is_expired())
        
        # Check ID format
        self.assertTrue(product.id.startswith("FOOD-"))
    
    def test_book_factory(self):
        """Test book product factory"""
        product = ProductFactory.create_book(
            name="Design Patterns",
            purchase_price=Decimal('25'),
            selling_price=Decimal('45'),
            quantity=30,
            author="Erich Gamma",
            isbn="978-0-201-63361-0"
            # Removed 'publisher' parameter
        )
        
        # Check product type
        self.assertIsInstance(product, BookProduct)
        self.assertEqual(product.name, "Design Patterns")
        self.assertEqual(product.category, ProductCategory.BOOKS)
        
        # Check specialized properties
        self.assertEqual(product.author, "Erich Gamma")
        self.assertEqual(product.isbn, "978-0-201-63361-0")
        # Publisher will be default value
        
        # Check ID format
        self.assertTrue(product.id.startswith("BOOK-"))

class TestDecoratorPattern(unittest.TestCase):
    """Test Decorator Pattern implementations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_product = Product(
            id="DECOR-TEST",
            name="Base Product",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(Decimal('100')),
            selling_price=Money(Decimal('150')),
            quantity=40,
            description="A basic product"
        )
    
    def test_discounted_product(self):
        """Test discounted product decorator"""
        # Apply 20% discount
        discounted = DiscountedProduct(self.base_product, Decimal('20'))
        
        # Check it's a decorator
        self.assertIsInstance(discounted, ProductDecorator)
        self.assertIsInstance(discounted, DiscountedProduct)
        
        # Check decorated product is accessible
        self.assertEqual(discounted.decorated_product, self.base_product)
        
        # Check details include discount information
        details = discounted.get_details()
        
        self.assertIn('original_price', details)
        self.assertIn('discounted_price', details)
        self.assertIn('discount_percentage', details)
        self.assertIn('savings', details)
        self.assertIn('decorated', details)
        self.assertIn('decorator_type', details)
        
        self.assertEqual(details['discount_percentage'], "20%")
        self.assertIn("USD 150.00", details['original_price'])
        self.assertIn("USD 120.00", details['discounted_price'])  # 150 * 0.8
        self.assertIn("USD 30.00", details['savings'])  # 150 - 120
        self.assertTrue(details['decorated'])
        self.assertEqual(details['decorator_type'], 'DiscountedProduct')
        
        # Check get_selling_price returns discounted price
        discounted_price = discounted.get_selling_price()
        self.assertEqual(discounted_price.amount, Decimal('120'))  # 150 * 0.8
    
    def test_featured_product(self):
        """Test featured product decorator"""
        featured = FeaturedProduct(
            self.base_product,
            "Product of the Month",
            "gold"
        )
        
        # Check details include featured information
        details = featured.get_details()
        
        self.assertIn('featured', details)
        self.assertIn('feature_description', details)
        self.assertIn('banner_color', details)
        self.assertIn('featured_since', details)
        
        self.assertTrue(details['featured'])
        self.assertEqual(details['feature_description'], "Product of the Month")
        self.assertEqual(details['banner_color'], "gold")
        self.assertIsNotNone(details['featured_since'])
    
    def test_multiple_decorators(self):
        """Test chaining multiple decorators"""
        # Apply discount then feature
        discounted = DiscountedProduct(self.base_product, Decimal('15'))
        featured_discounted = FeaturedProduct(discounted, "Special Offer")
        
        # Check it's still a decorator
        self.assertIsInstance(featured_discounted, ProductDecorator)
        self.assertIsInstance(featured_discounted, FeaturedProduct)
        
        # Check details include both decorations
        details = featured_discounted.get_details()
        
        self.assertIn('discount_percentage', details)
        self.assertIn('feature_description', details)
        self.assertEqual(details['discount_percentage'], "15%")
        self.assertEqual(details['feature_description'], "Special Offer")
        
        # Check property delegation still works
        self.assertEqual(featured_discounted.name, "Base Product")
        self.assertEqual(featured_discounted.category, ProductCategory.ELECTRONICS)
        self.assertEqual(featured_discounted.quantity, 40)
    
    def test_decorator_chain(self):
        """Test deep decorator chain"""
        # Create a chain: Base -> Discounted -> Featured -> Limited Edition (simulated)
        
        # First decorator
        chain = DiscountedProduct(self.base_product, Decimal('10'))
        
        # Second decorator
        chain = FeaturedProduct(chain, "Limited Time")
        
        # Check chain properties
        details = chain.get_details()
        
        self.assertIn('discount_percentage', details)
        self.assertIn('feature_description', details)
        self.assertEqual(details['discount_percentage'], "10%")
        self.assertEqual(details['feature_description'], "Limited Time")
        
        # Verify original product is accessible through chain
        original = chain.decorated_product.decorated_product
        self.assertEqual(original, self.base_product)

class TestSingletonPattern(unittest.TestCase):
    """Test Singleton Pattern implementation"""
    
    def test_singleton_instance(self):
        """Test that only one instance is created"""
        # Get first instance
        db1 = DatabaseConnection(":memory:")
        
        # Get second instance (should be same as first)
        db2 = DatabaseConnection(":memory:")
        
        # Get third instance using get_instance
        db3 = DatabaseConnection.get_instance()
        
        # All should be the same instance
        self.assertIs(db1, db2)
        self.assertIs(db1, db3)
        self.assertIs(db2, db3)
        
        # Test instance properties
        self.assertEqual(db1.db_path, ":memory:")
        self.assertIsNotNone(db1.connection)
        self.assertIsNotNone(db1.cursor)
    
    def test_database_operations(self):
        """Test database operations using singleton"""
        # Use in-memory database for testing
        db = DatabaseConnection(":memory:")
        
        try:
            # Test table creation (done in initialization)
            cursor = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Should have created tables
            table_names = [table[0] for table in tables]
            self.assertIn('products', table_names)
            self.assertIn('orders', table_names)
            self.assertIn('order_items', table_names)
            self.assertIn('employees', table_names)
            
            # Test data insertion
            db.execute_query(
                "INSERT INTO products (id, name, category, purchase_price, selling_price, quantity, sku, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("TEST-001", "Test Product", "Electronics", 100.0, 150.0, 50, "TEST-SKU", "2024-01-01", "2024-01-01")
            )
            db.commit()
            
            # Test data retrieval
            cursor = db.execute_query("SELECT * FROM products WHERE id = ?", ("TEST-001",))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row[1], "Test Product")  # name
            self.assertEqual(row[2], "Electronics")   # category
            self.assertEqual(row[5], 50)              # quantity
            
        finally:
            # Close connection
            db.close()
            # Reset singleton for next test
            DatabaseConnection._instance = None
    
    def test_singleton_reset(self):
        """Test singleton reset after close"""
        # Get instance
        db1 = DatabaseConnection(":memory:")
        
        # Close it
        db1.close()
        
        # Singleton should be reset
        self.assertIsNone(DatabaseConnection._instance)
        
        # Get new instance
        db2 = DatabaseConnection(":memory:")
        
        # Should be different instance
        self.assertIsNot(db1, db2)
        
        # Clean up
        db2.close()
        DatabaseConnection._instance = None

# ==================== TEST TEMPLATE METHOD PATTERN ====================

class TestTemplateMethodPattern(unittest.TestCase):
    """Test Template Method Pattern implementations"""
    
    def test_report_generator_structure(self):
        """Test report generator abstract class structure"""
        # Cannot instantiate abstract class
        with self.assertRaises(TypeError):
            generator = ReportGenerator()
    
    def test_concrete_report_generators(self):
        """Test concrete report generator implementations"""
        # Create mock repository
        class MockProductRepository:
            def get_all(self):
                return [
                    Product(
                        id="P1",
                        name="Product 1",
                        category=ProductCategory.ELECTRONICS,
                        purchase_price=Money(Decimal('100')),
                        selling_price=Money(Decimal('150')),
                        quantity=10  # Exactly at MIN_STOCK_LEVEL
                    ),
                    Product(
                        id="P2",
                        name="Product 2",
                        category=ProductCategory.CLOTHING,
                        purchase_price=Money(Decimal('50')),
                        selling_price=Money(Decimal('80')),
                        quantity=5  # Below MIN_STOCK_LEVEL
                    )
                ]
        
        # Test inventory report generator
        repo = MockProductRepository()
        generator = InventoryReportGenerator(repo)
        
        # Generate report
        report = generator.generate_report()
        
        # Check report structure
        self.assertIn('report_type', report)
        self.assertIn('generated_at', report)
        self.assertIn('data', report)
        
        self.assertEqual(report['report_type'], 'InventoryReportGenerator')
        self.assertIsNotNone(report['generated_at'])
        
        # Check data content
        data = report['data']
        self.assertEqual(data['total_products'], 2)
        self.assertEqual(data['low_stock_count'], 2)  # Both products have quantity <= 10
        self.assertIn('Electronics', data['category_summary'])
        self.assertIn('Clothing', data['category_summary'])

# ==================== TEST USE CASES ====================

class TestProductManagementUseCase(unittest.TestCase):
    """Test Product Management Use Case"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock repository
        class MockRepository(ProductRepository):
            def __init__(self):
                self.products = {}
                self.save_calls = []
                self.get_all_calls = 0
            
            def save(self, product):
                self.products[product.id] = product
                self.save_calls.append(product.id)
            
            def get_by_id(self, product_id):
                return self.products.get(product_id)
            
            def get_all(self):
                self.get_all_calls += 1
                return list(self.products.values())
            
            def delete(self, product_id):
                if product_id in self.products:
                    del self.products[product_id]
                    return True
                return False
            
            def search_by_name(self, name):
                return [p for p in self.products.values() if name.lower() in p.name.lower()]
            
            def get_by_category(self, category):
                return [p for p in self.products.values() if p.category == category]
            
            def get_low_stock_products(self):
                return [p for p in self.products.values() if p.is_low_stock()]
            
            def get_by_price_range(self, min_price, max_price):
                return [p for p in self.products.values() 
                       if min_price <= p.selling_price.amount <= max_price]
        
        self.repository = MockRepository()
        self.use_case = ProductManagementUseCase(self.repository)
    
    def test_create_product(self):
        """Test creating a product"""
        product = self.use_case.create_product(
            name="New Laptop",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('800'),
            selling_price=Decimal('1200'),
            quantity=25,
            description="A powerful laptop"
        )
        
        # Check product was created
        self.assertIsInstance(product, Product)
        self.assertEqual(product.name, "New Laptop")
        self.assertEqual(product.category, ProductCategory.ELECTRONICS)
        self.assertEqual(product.purchase_price.amount, Decimal('800'))
        self.assertEqual(product.selling_price.amount, Decimal('1200'))
        self.assertEqual(product.quantity, 25)
        self.assertEqual(product.description, "A powerful laptop")
        
        # Check product was saved
        self.assertIn(product.id, self.repository.products)
        self.assertIn(product.id, self.repository.save_calls)
        
        # Check we can retrieve it
        retrieved = self.repository.get_by_id(product.id)
        self.assertEqual(retrieved, product)
        
    def test_update_product_price(self):
        """Test updating product price"""
        # First create a product
        product = self.use_case.create_product(
            name="Test Product",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('100'),
            selling_price=Decimal('150'),
            quantity=10
        )
        
        # Update price
        updated = self.use_case.update_product_price(product.id, Decimal('180'))
        
        # Check price was updated
        self.assertEqual(updated.selling_price.amount, Decimal('180'))
        
        # Check product was saved again
        self.assertEqual(self.repository.save_calls.count(product.id), 2)
    
    def test_restock_product(self):
        """Test restocking a product"""
        # Create a product with low stock
        product = self.use_case.create_product(
            name="Low Stock Item",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('50'),
            selling_price=Decimal('75'),
            quantity=5  # Low stock
        )
        
        # Restock
        restocked = self.use_case.restock_product(product.id, 20)
        
        # Check quantity increased
        self.assertEqual(restocked.quantity, 25)
        
        # Check product was saved
        self.assertEqual(self.repository.save_calls.count(product.id), 2)
    
    def test_get_low_stock_products(self):
        """Test getting low stock products"""
        # Create products with different stock levels
        self.use_case.create_product(
            name="Low Stock 1",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('100'),
            selling_price=Decimal('150'),
            quantity=5  # Low stock
        )
        
        self.use_case.create_product(
            name="Normal Stock",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('100'),
            selling_price=Decimal('150'),
            quantity=50  # Normal stock
        )
        
        self.use_case.create_product(
            name="Low Stock 2",
            category=ProductCategory.CLOTHING,
            purchase_price=Decimal('20'),
            selling_price=Decimal('40'),
            quantity=8  # Low stock
        )
        
        # Get low stock products
        low_stock = self.use_case.get_low_stock_products()
        
        # Should have 2 low stock products
        self.assertEqual(len(low_stock), 2)
        
        # Check they are actually low stock
        for product in low_stock:
            self.assertTrue(product.is_low_stock())
    
    def test_calculate_inventory_value(self):
        """Test calculating total inventory value"""
        # Create products
        self.use_case.create_product(
            name="Product 1",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('100'),
            selling_price=Decimal('150'),
            quantity=10  # Value: 100 * 10 = 1000
        )
        
        self.use_case.create_product(
            name="Product 2",
            category=ProductCategory.CLOTHING,
            purchase_price=Decimal('50'),
            selling_price=Decimal('80'),
            quantity=20  # Value: 50 * 20 = 1000
        )
        
        # Calculate total value
        total_value = self.use_case.calculate_inventory_value()
        
        # Should be 2000 (1000 + 1000)
        self.assertEqual(total_value.amount, Decimal('2000'))
    
    def test_search_products(self):
        """Test searching products by name"""
        # Create products
        self.use_case.create_product(
            name="Laptop Pro",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('1000'),
            selling_price=Decimal('1500'),
            quantity=5
        )
        
        self.use_case.create_product(
            name="Gaming Mouse",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('50'),
            selling_price=Decimal('80'),
            quantity=15
        )
        
        self.use_case.create_product(
            name="Keyboard",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('60'),
            selling_price=Decimal('90'),
            quantity=8
        )
        
        # Search for "lap"
        results = self.use_case.search_products("lap")
        
        # Should find "Laptop Pro"
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Laptop Pro")
        
        # Search for "mouse"
        results = self.use_case.search_products("mouse")
        
        # Should find "Gaming Mouse"
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Gaming Mouse")
    
    def test_get_products_by_category(self):
        """Test getting products by category"""
        # Create products in different categories
        self.use_case.create_product(
            name="Laptop",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('1000'),
            selling_price=Decimal('1500'),
            quantity=5
        )
        
        self.use_case.create_product(
            name="T-Shirt",
            category=ProductCategory.CLOTHING,
            purchase_price=Decimal('20'),
            selling_price=Decimal('40'),
            quantity=50
        )
        
        self.use_case.create_product(
            name="Smartphone",
            category=ProductCategory.ELECTRONICS,
            purchase_price=Decimal('500'),
            selling_price=Decimal('750'),
            quantity=15
        )
        
        # Get electronics products
        electronics = self.use_case.get_products_by_category(ProductCategory.ELECTRONICS)
        
        # Should have 2 electronics products
        self.assertEqual(len(electronics), 2)
        
        # Check they are all electronics
        for product in electronics:
            self.assertEqual(product.category, ProductCategory.ELECTRONICS)

# ==================== TEST SUITE RUNNER ====================

def run_all_tests():
    """Run all unit tests"""
    # Create test suite
    test_cases = [
        # Value Objects
        TestMoney,
        TestAddress,
        
        # Enums
        TestProductCategory,
        TestOrderStatus,
        TestEmployeeRole,
        
        # Entities
        TestProductEntity,
        TestClothingProduct,
        TestFoodProduct,
        TestBookProduct,
        TestOrderEntity,
        TestEmployeeEntity,
        TestOrderItem,
        
        # Design Patterns
        TestStrategyPattern,
        TestObserverPattern,
        TestFactoryPattern,
        TestDecoratorPattern,
        TestSingletonPattern,
        TestTemplateMethodPattern,
        
        # Use Cases
        TestProductManagementUseCase,
    ]
    
    # Create test suite
    suite = unittest.TestSuite()
    
    for test_case in test_cases:
        tests = unittest.defaultTestLoader.loadTestsFromTestCase(test_case)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Successful: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")
        
        # Print failures
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"\n{test}:")
                print(traceback)
        
        # Print errors
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"\n{test}:")
                print(traceback)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)