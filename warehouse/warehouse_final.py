"""
===============================================================================
WAREHOUSE MANAGEMENT SYSTEM - FINAL VERSION
Course Project for OOP & VVRPO - 2024
Clean Architecture Implementation with GoF Design Patterns
===============================================================================
"""

# ==================== IMPORTS ====================
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field, asdict
from decimal import Decimal
import uuid
import json
import sqlite3
import csv
import os

# ==================== DESIGN PATTERNS (GoF) ====================

# ---------- 1. STRATEGY PATTERN ----------
class PricingStrategy(ABC):
    """Strategy Pattern: Interface for different pricing calculations"""
    
    @abstractmethod
    def calculate_total(self, price: Decimal, quantity: int) -> Decimal:
        """Calculate total price based on strategy"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get strategy description"""
        pass

class RegularPricing(PricingStrategy):
    """Regular pricing strategy (no discount)"""
    
    def calculate_total(self, price: Decimal, quantity: int) -> Decimal:
        return price * quantity
    
    def get_description(self) -> str:
        return "Regular Pricing (No Discount)"

class BulkDiscountPricing(PricingStrategy):
    """Bulk discount pricing strategy"""
    
    def __init__(self, discount_rate: Decimal = Decimal('0.1'), min_quantity: int = 50):
        self.discount_rate = discount_rate
        self.min_quantity = min_quantity
    
    def calculate_total(self, price: Decimal, quantity: int) -> Decimal:
        if quantity >= self.min_quantity:
            return (price * quantity) * (Decimal('1') - self.discount_rate)
        return price * quantity
    
    def get_description(self) -> str:
        return f"Bulk Discount ({self.discount_rate*100}% off for {self.min_quantity}+ items)"

class SeasonalPricing(PricingStrategy):
    """Seasonal/holiday pricing strategy"""
    
    def __init__(self, seasonal_multiplier: Decimal = Decimal('1.2')):
        self.seasonal_multiplier = seasonal_multiplier
    
    def calculate_total(self, price: Decimal, quantity: int) -> Decimal:
        return (price * quantity) * self.seasonal_multiplier
    
    def get_description(self) -> str:
        if self.seasonal_multiplier > Decimal('1'):
            return f"Seasonal Pricing (+{(self.seasonal_multiplier - Decimal('1'))*100}% increase)"
        else:
            return f"Seasonal Pricing ({(Decimal('1') - self.seasonal_multiplier)*100}% discount)"

# ---------- 2. OBSERVER PATTERN ----------
class InventoryObserver(ABC):
    """Observer Pattern: Interface for inventory notifications"""
    
    @abstractmethod
    def update(self, product_id: str, product_name: str, 
               quantity: int, threshold: int):
        """Receive update notification"""
        pass
    
    @abstractmethod
    def get_observer_type(self) -> str:
        """Get observer type"""
        pass

class EmailNotifier(InventoryObserver):
    """Concrete observer for email notifications"""
    
    def __init__(self, email_address: str):
        self.email_address = email_address
        self.notification_count = 0
    
    def update(self, product_id: str, product_name: str, 
               quantity: int, threshold: int):
        self.notification_count += 1
        print(f"[EMAIL to {self.email_address}] ALERT: Product '{product_name}' "
              f"(ID: {product_id}) is low on stock: {quantity} < {threshold}")
    
    def get_observer_type(self) -> str:
        return "Email Notifier"

class LogNotifier(InventoryObserver):
    """Concrete observer for logging"""
    
    def __init__(self, log_file: str = "inventory.log"):
        self.log_file = log_file
        self.notifications = []
    
    def update(self, product_id: str, product_name: str, 
               quantity: int, threshold: int):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'product_id': product_id,
            'product_name': product_name,
            'quantity': quantity,
            'threshold': threshold,
            'message': f"Low stock alert: {product_name} - {quantity} units remaining"
        }
        self.notifications.append(log_entry)
        
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(f"{log_entry['timestamp']} - {log_entry['message']}\n")
        
        print(f"[LOG] Low stock alert logged for {product_name}")
    
    def get_observer_type(self) -> str:
        return "Log Notifier"

class DashboardNotifier(InventoryObserver):
    """Concrete observer for dashboard updates"""
    
    def __init__(self):
        self.alerts = []
    
    def update(self, product_id: str, product_name: str, 
               quantity: int, threshold: int):
        alert = {
            'id': product_id,
            'name': product_name,
            'current': quantity,
            'threshold': threshold,
            'time': datetime.now().isoformat()
        }
        self.alerts.append(alert)
        print(f"[DASHBOARD] Alert added: {product_name} - Low stock")
    
    def get_observer_type(self) -> str:
        return "Dashboard Notifier"

# ---------- 3. FACTORY PATTERN ----------
class ProductFactory:
    """Factory Pattern: Creates Product objects with different configurations"""
    
    @staticmethod
    def create_electronics(name: str, purchase_price: Decimal, 
                          selling_price: Decimal, quantity: int) -> 'Product':
        """Create electronics product with auto-generated ID"""
        product_id = f"ELEC-{uuid.uuid4().hex[:8].upper()}"
        return Product(
            id=product_id,
            name=name,
            category=ProductCategory.ELECTRONICS,
            purchase_price=Money(purchase_price),
            selling_price=Money(selling_price),
            quantity=quantity
        )
    
    @staticmethod
    def create_clothing(name: str, purchase_price: Decimal, 
                       selling_price: Decimal, quantity: int, 
                       size: str = "M", color: str = "Black") -> 'ClothingProduct':
        """Create clothing product with additional attributes"""
        product_id = f"CLOTH-{uuid.uuid4().hex[:8].upper()}"
        return ClothingProduct(
            id=product_id,
            name=name,
            category=ProductCategory.CLOTHING,
            purchase_price=Money(purchase_price),
            selling_price=Money(selling_price),
            quantity=quantity,
            size=size,
            color=color
        )
    
    @staticmethod
    def create_food(name: str, purchase_price: Decimal, 
                   selling_price: Decimal, quantity: int, 
                   expiration_date: date = None) -> 'FoodProduct':
        """Create food product with expiration date"""
        product_id = f"FOOD-{uuid.uuid4().hex[:8].upper()}"
        return FoodProduct(
            id=product_id,
            name=name,
            category=ProductCategory.FOOD,
            purchase_price=Money(purchase_price),
            selling_price=Money(selling_price),
            quantity=quantity,
            expiration_date=expiration_date
        )
    
    @staticmethod
    def create_book(name: str, purchase_price: Decimal, 
                   selling_price: Decimal, quantity: int,
                   author: str = "Unknown", isbn: str = "") -> 'BookProduct':
        """Create book product with author and ISBN"""
        product_id = f"BOOK-{uuid.uuid4().hex[:8].upper()}"
        return BookProduct(
            id=product_id,
            name=name,
            category=ProductCategory.BOOKS,
            purchase_price=Money(purchase_price),
            selling_price=Money(selling_price),
            quantity=quantity,
            author=author,
            isbn=isbn
        )

# ---------- 4. DECORATOR PATTERN ----------
class ProductDecorator(ABC):
    """Decorator Pattern: Base decorator for adding features to products"""
    
    def __init__(self, product: 'Product'):
        self._product = product
    
    @property
    def decorated_product(self) -> 'Product':
        return self._product
    
    def get_details(self) -> Dict[str, Any]:
        """Get decorated product details"""
        details = self._product.get_details()
        details['decorated'] = True
        details['decorator_type'] = self.__class__.__name__
        return details
    
    def __getattr__(self, name):
        """Delegate unknown attributes to wrapped product"""
        return getattr(self._product, name)

class DiscountedProduct(ProductDecorator):
    """Add discount to product"""
    
    def __init__(self, product: 'Product', discount_percentage: Decimal):
        super().__init__(product)
        self.discount_percentage = discount_percentage
    
    def get_details(self) -> Dict[str, Any]:
        details = super().get_details()
        original_price = self._product.selling_price.amount
        discounted_price = original_price * (Decimal('1') - self.discount_percentage/Decimal('100'))
        details['original_price'] = str(self._product.selling_price)
        details['discounted_price'] = str(Money(discounted_price))
        details['discount_percentage'] = f"{self.discount_percentage}%"
        details['savings'] = str(Money(original_price - discounted_price))
        return details
    
    def get_selling_price(self) -> 'Money':
        """Override selling price with discount"""
        original_price = self._product.selling_price.amount
        discounted_price = original_price * (Decimal('1') - self.discount_percentage/Decimal('100'))
        return Money(discounted_price)

class FeaturedProduct(ProductDecorator):
    """Mark product as featured"""
    
    def __init__(self, product: 'Product', feature_description: str, 
                 banner_color: str = "gold"):
        super().__init__(product)
        self.feature_description = feature_description
        self.banner_color = banner_color
    
    def get_details(self) -> Dict[str, Any]:
        details = super().get_details()
        details['featured'] = True
        details['feature_description'] = self.feature_description
        details['banner_color'] = self.banner_color
        details['featured_since'] = datetime.now().isoformat()
        return details

class LimitedEditionProduct(ProductDecorator):
    """Mark product as limited edition"""
    
    def __init__(self, product: 'Product', edition_number: int, 
                 total_edition: int = 1000):
        super().__init__(product)
        self.edition_number = edition_number
        self.total_edition = total_edition
    
    def get_details(self) -> Dict[str, Any]:
        details = super().get_details()
        details['limited_edition'] = True
        details['edition_number'] = self.edition_number
        details['total_edition'] = self.total_edition
        details['rarity'] = f"{self.edition_number}/{self.total_edition}"
        return details

# ---------- 5. SINGLETON PATTERN ----------
class DatabaseConnection:
    """Singleton Pattern: Single database connection instance"""
    
    _instance = None
    
    def __new__(cls, db_path: str = "warehouse.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(db_path)
        return cls._instance
    
    def _initialize(self, db_path: str):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self._init_tables()
    
    def _init_tables(self):
        """Initialize database tables"""
        # Products table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                purchase_price REAL NOT NULL,
                selling_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                sku TEXT,
                attributes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Orders table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                shipping_address TEXT,
                status TEXT NOT NULL,
                total_amount REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Order items table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                unit_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            )
        """)
        
        # Employees table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                salary REAL NOT NULL,
                hire_date TEXT NOT NULL,
                tasks TEXT
            )
        """)
        
        self.connection.commit()
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute SQL query"""
        return self.cursor.execute(query, params)
    
    def commit(self):
        """Commit transaction"""
        self.connection.commit()
    
    def close(self):
        """Close connection (use carefully in singleton)"""
        self.connection.close()
        DatabaseConnection._instance = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls()
        return cls._instance

# ---------- 6. TEMPLATE METHOD PATTERN ----------
class ReportGenerator(ABC):
    """Template Method Pattern: Base class for report generation"""
    
    def generate_report(self) -> Dict[str, Any]:
        """Template method defining the algorithm structure"""
        self._validate_data()
        data = self._collect_data()
        processed_data = self._process_data(data)
        report = self._format_report(processed_data)
        self._save_report(report)
        return report
    
    @abstractmethod
    def _collect_data(self) -> Any:
        """Collect data for report (to be implemented by subclasses)"""
        pass
    
    @abstractmethod
    def _process_data(self, data: Any) -> Any:
        """Process collected data (to be implemented by subclasses)"""
        pass
    
    def _validate_data(self):
        """Validate data before processing (hook method)"""
        print(f"Validating data for {self.__class__.__name__}...")
    
    def _format_report(self, data: Any) -> Dict[str, Any]:
        """Format the report (default implementation)"""
        return {
            'report_type': self.__class__.__name__,
            'generated_at': datetime.now().isoformat(),
            'data': data
        }
    
    def _save_report(self, report: Dict[str, Any]):
        """Save report (hook method)"""
        print(f"Report generated: {report['report_type']}")

class InventoryReportGenerator(ReportGenerator):
    """Concrete report generator for inventory"""
    
    def __init__(self, product_repository: 'ProductRepository'):
        self.product_repository = product_repository
    
    def _collect_data(self) -> List['Product']:
        """Collect all products"""
        return self.product_repository.get_all()
    
    def _process_data(self, products: List['Product']) -> Dict[str, Any]:
        """Process inventory data"""
        total_products = len(products)
        total_value = Money(Decimal('0'))
        low_stock_count = 0
        category_summary = {}
        
        for product in products:
            total_value = total_value + product.calculate_total_value()
            if product.is_low_stock():
                low_stock_count += 1
            
            category = product.category.value
            category_summary[category] = category_summary.get(category, 0) + 1
        
        return {
            'total_products': total_products,
            'total_value': str(total_value),
            'low_stock_count': low_stock_count,
            'category_summary': category_summary,
            'generation_date': date.today().isoformat()
        }

class SalesReportGenerator(ReportGenerator):
    """Concrete report generator for sales"""
    
    def __init__(self, order_repository: 'OrderRepository'):
        self.order_repository = order_repository
    
    def _collect_data(self) -> List['Order']:
        """Collect all orders"""
        return self.order_repository.get_all()
    
    def _process_data(self, orders: List['Order']) -> Dict[str, Any]:
        """Process sales data"""
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.status == OrderStatus.DELIVERED])
        total_revenue = Money(Decimal('0'))
        
        for order in orders:
            if order.status == OrderStatus.DELIVERED:
                total_revenue = total_revenue + order.calculate_total()
        
        return {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_revenue': str(total_revenue),
            'completion_rate': f"{(completed_orders/total_orders*100):.1f}%" if total_orders > 0 else "0%"
        }

# ==================== DOMAIN LAYER ====================

# ---------- Value Objects ----------
@dataclass(frozen=True)
class Money:
    """Value object for monetary values"""
    amount: Decimal
    currency: str = "USD"
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, quantity: int) -> 'Money':
        return Money(self.amount * quantity, self.currency)
    
    def __truediv__(self, divisor: int) -> 'Money':
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / divisor, self.currency)
    
    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
    
    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"

@dataclass(frozen=True)
class Address:
    """Value object for addresses"""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    
    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}, {self.country}"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Address':
        return cls(**data)

# ---------- Enums ----------
class ProductCategory(Enum):
    """Product category enumeration"""
    ELECTRONICS = "Electronics"
    CLOTHING = "Clothing"
    FOOD = "Food"
    BOOKS = "Books"
    FURNITURE = "Furniture"
    SPORTS = "Sports"
    BEAUTY = "Beauty"
    
    @classmethod
    def all_categories(cls) -> List[str]:
        return [category.value for category in cls]

class OrderStatus(Enum):
    """Order status lifecycle enumeration"""
    DRAFT = "Draft"
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"
    
    @classmethod
    def can_transition(cls, current: 'OrderStatus', new: 'OrderStatus') -> bool:
        """Validate status transition rules"""
        valid_transitions = {
            cls.DRAFT: [cls.PENDING, cls.CANCELLED],
            cls.PENDING: [cls.CONFIRMED, cls.CANCELLED],
            cls.CONFIRMED: [cls.PROCESSING, cls.CANCELLED],
            cls.PROCESSING: [cls.SHIPPED, cls.CANCELLED],
            cls.SHIPPED: [cls.DELIVERED],
            cls.DELIVERED: [cls.REFUNDED],
            cls.CANCELLED: [],
            cls.REFUNDED: []
        }
        return new in valid_transitions.get(current, [])
    
    @classmethod
    def is_terminal_status(cls, status: 'OrderStatus') -> bool:
        """Check if status is terminal (no further transitions)"""
        return status in [cls.DELIVERED, cls.CANCELLED, cls.REFUNDED]

class EmployeeRole(Enum):
    """Employee roles with permissions"""
    MANAGER = "Manager"
    SUPERVISOR = "Supervisor"
    WAREHOUSE_WORKER = "Warehouse Worker"
    ACCOUNTANT = "Accountant"
    SALES_REP = "Sales Representative"
    SUPPORT = "Customer Support"
    ADMIN = "Administrator"
    
    def get_permissions(self) -> Set[str]:
        """Get permissions for this role"""
        permissions = {
            self.MANAGER: {
                "view_all", "edit_all", "delete_all", 
                "manage_employees", "view_reports", "approve_orders"
            },
            self.SUPERVISOR: {
                "view_all", "edit_products", "manage_orders", 
                "view_reports", "manage_inventory"
            },
            self.WAREHOUSE_WORKER: {
                "view_products", "manage_inventory", "view_orders", 
                "update_order_status"
            },
            self.ACCOUNTANT: {
                "view_reports", "view_orders", "view_products", 
                "financial_operations"
            },
            self.SALES_REP: {
                "view_products", "create_orders", "view_customers", 
                "update_customer_info"
            },
            self.SUPPORT: {
                "view_products", "view_orders", "update_order_status", 
                "view_customers"
            },
            self.ADMIN: {
                "view_all", "edit_all", "delete_all", 
                "manage_system", "configure_settings"
            }
        }
        return permissions.get(self, set())
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has specific permission"""
        return permission in self.get_permissions()

# ---------- Base Entity ----------
class Entity(ABC):
    """Abstract base class for all domain entities"""
    
    def __init__(self, id: str):
        if not id or not isinstance(id, str):
            raise ValueError("Entity ID must be a non-empty string")
        self._id = id
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def _update_timestamp(self):
        """Update the updated_at timestamp"""
        self._updated_at = datetime.now()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

# ---------- Product Entity ----------
class Product(Entity):
    """Product domain entity with business rules"""
    
    MIN_STOCK_LEVEL = 10
    MAX_STOCK_LEVEL = 1000
    WARNING_STOCK_LEVEL = 50
    
    def __init__(self, 
                 id: str,
                 name: str,
                 category: ProductCategory,
                 purchase_price: Money,
                 selling_price: Money,
                 quantity: int,
                 sku: str = "",
                 description: str = "",
                 weight: Decimal = Decimal('0'),
                 dimensions: Dict[str, Decimal] = None):
        super().__init__(id)
        self._name = name
        self._category = category
        self._purchase_price = purchase_price
        self._selling_price = selling_price
        self._quantity = quantity
        self._sku = sku or self._generate_sku()
        self._description = description
        self._weight = weight
        self._dimensions = dimensions or {}
        self._observers: List[InventoryObserver] = []
        
        self._validate()
    
    def _validate(self):
        """Validate product business rules"""
        if not self._name or len(self._name) < 2:
            raise ValueError("Product name must be at least 2 characters")
        
        if self._quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        if self._quantity > self.MAX_STOCK_LEVEL:
            raise ValueError(f"Quantity cannot exceed {self.MAX_STOCK_LEVEL}")
        
        if self._selling_price.amount <= 0:
            raise ValueError("Selling price must be positive")
        
        if self._purchase_price.amount <= 0:
            raise ValueError("Purchase price must be positive")
        
        if self._selling_price.amount < self._purchase_price.amount:
            raise ValueError("Selling price cannot be less than purchase price")
    
    def _generate_sku(self) -> str:
        """Generate SKU from product information"""
        category_code = self._category.name[:3].upper()
        random_part = str(uuid.uuid4())[:6].upper()
        return f"{category_code}-{random_part}"
    
    # ---------- Properties ----------
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        if len(value) < 2:
            raise ValueError("Product name must be at least 2 characters")
        self._name = value
        self._update_timestamp()
    
    @property
    def category(self) -> ProductCategory:
        return self._category
    
    @property
    def purchase_price(self) -> Money:
        return self._purchase_price
    
    @purchase_price.setter
    def purchase_price(self, value: Money):
        if value.amount <= 0:
            raise ValueError("Purchase price must be positive")
        self._purchase_price = value
        self._update_timestamp()
    
    @property
    def selling_price(self) -> Money:
        return self._selling_price
    
    @selling_price.setter
    def selling_price(self, value: Money):
        if value.amount <= 0:
            raise ValueError("Selling price must be positive")
        if value.amount < self._purchase_price.amount:
            raise ValueError("Selling price cannot be less than purchase price")
        self._selling_price = value
        self._update_timestamp()
    
    @property
    def quantity(self) -> int:
        return self._quantity
    
    @property
    def sku(self) -> str:
        return self._sku
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str):
        self._description = value
        self._update_timestamp()
    
    @property
    def weight(self) -> Decimal:
        return self._weight
    
    @property
    def dimensions(self) -> Dict[str, Decimal]:
        return self._dimensions.copy()
    
    # ---------- Observer Pattern Methods ----------
    def attach_observer(self, observer: InventoryObserver):
        """Attach inventory observer"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach_observer(self, observer: InventoryObserver):
        """Detach inventory observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self):
        """Notify all observers about low stock"""
        if self.is_low_stock():
            for observer in self._observers:
                observer.update(
                    self.id,
                    self.name,
                    self.quantity,
                    self.MIN_STOCK_LEVEL
                )
    
    # ---------- Business Methods ----------
    def increase_quantity(self, amount: int) -> None:
        """Increase product quantity with validation"""
        if amount < 0:
            raise ValueError("Amount must be positive")
        
        if self._quantity + amount > self.MAX_STOCK_LEVEL:
            raise ValueError(f"Cannot exceed max stock level of {self.MAX_STOCK_LEVEL}")
        
        self._quantity += amount
        self._update_timestamp()
        self._notify_observers()
    
    def decrease_quantity(self, amount: int) -> None:
        """Decrease product quantity with validation"""
        if amount < 0:
            raise ValueError("Amount must be positive")
        
        if self._quantity - amount < 0:
            raise ValueError("Insufficient stock")
        
        self._quantity -= amount
        self._update_timestamp()
        self._notify_observers()
    
    def calculate_total_value(self) -> Money:
        """Calculate total inventory value (purchase price * quantity)"""
        return self._purchase_price * self._quantity
    
    def calculate_profit_margin(self) -> Decimal:
        """Calculate profit margin percentage"""
        if self._purchase_price.amount == 0:
            return Decimal(0)
        
        profit = self._selling_price.amount - self._purchase_price.amount
        return (profit / self._purchase_price.amount) * Decimal(100)
    
    def is_low_stock(self) -> bool:
        """Check if product is low on stock"""
        return self._quantity <= self.MIN_STOCK_LEVEL
    
    def is_warning_stock(self) -> bool:
        """Check if product is at warning stock level"""
        return self.MIN_STOCK_LEVEL < self._quantity <= self.WARNING_STOCK_LEVEL
    
    def can_fulfill_order(self, quantity: int) -> bool:
        """Check if product can fulfill order quantity"""
        return self._quantity >= quantity
    
    def get_stock_status(self) -> str:
        """Get human-readable stock status"""
        if self.is_low_stock():
            return "LOW STOCK"
        elif self.is_warning_stock():
            return "WARNING"
        else:
            return "IN STOCK"
    
    def get_details(self) -> Dict[str, Any]:
        """Get product details for presentation"""
        return {
            'id': self.id,
            'name': self._name,
            'category': self._category.value,
            'sku': self._sku,
            'description': self._description,
            'purchase_price': str(self._purchase_price),
            'selling_price': str(self._selling_price),
            'quantity': self._quantity,
            'stock_status': self.get_stock_status(),
            'total_value': str(self.calculate_total_value()),
            'profit_margin': f"{self.calculate_profit_margin():.2f}%",
            'weight': str(self._weight),
            'dimensions': self._dimensions,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
    
    def apply_pricing_strategy(self, strategy: PricingStrategy, quantity: int) -> Money:
        """Apply pricing strategy to calculate total"""
        total_amount = strategy.calculate_total(self._selling_price.amount, quantity)
        return Money(total_amount)
    
    def __str__(self) -> str:
        return f"Product: {self._name} ({self._category.value}) - Qty: {self._quantity} - Price: {self._selling_price}"
    
    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self._name}, category={self._category}, quantity={self._quantity})"

# ---------- Specialized Product Classes ----------
class ClothingProduct(Product):
    """Specialized product for clothing items"""
    
    def __init__(self, 
                 id: str,
                 name: str,
                 category: ProductCategory,
                 purchase_price: Money,
                 selling_price: Money,
                 quantity: int,
                 size: str = "M",
                 color: str = "Black",
                 material: str = "Cotton",
                 sku: str = "",
                 description: str = ""):
        super().__init__(id, name, category, purchase_price, selling_price, 
                        quantity, sku, description)
        self._size = size
        self._color = color
        self._material = material
    
    @property
    def size(self) -> str:
        return self._size
    
    @property
    def color(self) -> str:
        return self._color
    
    @property
    def material(self) -> str:
        return self._material
    
    def get_details(self) -> Dict[str, Any]:
        details = super().get_details()
        details.update({
            'size': self._size,
            'color': self._color,
            'material': self._material,
            'product_type': 'Clothing'
        })
        return details

class FoodProduct(Product):
    """Specialized product for food items"""
    
    def __init__(self, 
                 id: str,
                 name: str,
                 category: ProductCategory,
                 purchase_price: Money,
                 selling_price: Money,
                 quantity: int,
                 expiration_date: date = None,
                 sku: str = "",
                 description: str = "",
                 storage_temperature: Decimal = Decimal('4')):  # Celsius
        super().__init__(id, name, category, purchase_price, selling_price, 
                        quantity, sku, description)
        self._expiration_date = expiration_date
        self._storage_temperature = storage_temperature
    
    @property
    def expiration_date(self) -> Optional[date]:
        return self._expiration_date
    
    @property
    def storage_temperature(self) -> Decimal:
        return self._storage_temperature
    
    def is_expired(self) -> bool:
        """Check if food product is expired"""
        if not self._expiration_date:
            return False
        return date.today() > self._expiration_date
    
    def days_until_expiration(self) -> Optional[int]:
        """Calculate days until expiration"""
        if not self._expiration_date:
            return None
        delta = self._expiration_date - date.today()
        return delta.days if delta.days >= 0 else 0
    
    def get_details(self) -> Dict[str, Any]:
        details = super().get_details()
        details.update({
            'expiration_date': self._expiration_date.isoformat() if self._expiration_date else None,
            'is_expired': self.is_expired(),
            'days_until_expiration': self.days_until_expiration(),
            'storage_temperature': str(self._storage_temperature),
            'product_type': 'Food'
        })
        return details

class BookProduct(Product):
    """Specialized product for books"""
    
    def __init__(self, 
                 id: str,
                 name: str,
                 category: ProductCategory,
                 purchase_price: Money,
                 selling_price: Money,
                 quantity: int,
                 author: str = "Unknown",
                 isbn: str = "",
                 publisher: str = "",
                 publication_year: int = None,
                 sku: str = "",
                 description: str = ""):
        super().__init__(id, name, category, purchase_price, selling_price, 
                        quantity, sku, description)
        self._author = author
        self._isbn = isbn
        self._publisher = publisher
        self._publication_year = publication_year
    
    @property
    def author(self) -> str:
        return self._author
    
    @property
    def isbn(self) -> str:
        return self._isbn
    
    @property
    def publisher(self) -> str:
        return self._publisher
    
    @property
    def publication_year(self) -> Optional[int]:
        return self._publication_year
    
    def get_details(self) -> Dict[str, Any]:
        details = super().get_details()
        details.update({
            'author': self._author,
            'isbn': self._isbn,
            'publisher': self._publisher,
            'publication_year': self._publication_year,
            'product_type': 'Book'
        })
        return details

# ---------- OrderItem Value Object ----------
@dataclass
class OrderItem:
    """Value object for order line items"""
    product_id: str
    product_name: str
    unit_price: Money
    quantity: int
    total_price: Money = field(init=False)
    
    def __post_init__(self):
        """Validate order item"""
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.unit_price.amount <= 0:
            raise ValueError("Unit price must be positive")
        self.total_price = self.unit_price * self.quantity
    
    def calculate_total(self) -> Money:
        """Calculate total for this item"""
        return self.unit_price * self.quantity
    
    def increase_quantity(self, amount: int) -> None:
        """Increase item quantity"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.quantity += amount
        self.total_price = self.calculate_total()
    
    def decrease_quantity(self, amount: int) -> None:
        """Decrease item quantity"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if self.quantity - amount < 0:
            raise ValueError("Cannot decrease below zero")
        self.quantity -= amount
        self.total_price = self.calculate_total()
    
    def update_price(self, new_price: Money):
        """Update unit price"""
        if new_price.amount <= 0:
            raise ValueError("Unit price must be positive")
        self.unit_price = new_price
        self.total_price = self.calculate_total()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'unit_price': str(self.unit_price),
            'quantity': self.quantity,
            'total_price': str(self.total_price)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderItem':
        """Create from dictionary"""
        # Parse Money from string
        unit_price_str = data['unit_price']
        currency = unit_price_str.split()[0]
        amount = Decimal(unit_price_str.split()[1])
        unit_price = Money(amount, currency)
        
        return cls(
            product_id=data['product_id'],
            product_name=data['product_name'],
            unit_price=unit_price,
            quantity=data['quantity']
        )
    
    def __str__(self) -> str:
        return f"{self.product_name} x{self.quantity} @ {self.unit_price} = {self.total_price}"

# ---------- Order Entity ----------
class Order(Entity):
    """Order domain entity with business rules"""
    
    def __init__(self,
                 id: str,
                 customer_name: str,
                 customer_email: str,
                 shipping_address: Address = None,
                 billing_address: Address = None):
        super().__init__(id)
        self._customer_name = customer_name
        self._customer_email = customer_email
        self._shipping_address = shipping_address
        self._billing_address = billing_address or shipping_address
        self._status = OrderStatus.DRAFT
        self._items: Dict[str, OrderItem] = {}  # product_id -> OrderItem
        self._notes: str = ""
        
        self._validate()
    
    def _validate(self):
        """Validate order business rules"""
        if not self._customer_name or len(self._customer_name) < 2:
            raise ValueError("Customer name must be at least 2 characters")
        
        if '@' not in self._customer_email:
            raise ValueError("Invalid email address")
    
    # ---------- Properties ----------
    @property
    def customer_name(self) -> str:
        return self._customer_name
    
    @property
    def customer_email(self) -> str:
        return self._customer_email
    
    @property
    def shipping_address(self) -> Optional[Address]:
        return self._shipping_address
    
    @shipping_address.setter
    def shipping_address(self, address: Address):
        self._shipping_address = address
        self._update_timestamp()
    
    @property
    def billing_address(self) -> Optional[Address]:
        return self._billing_address
    
    @billing_address.setter
    def billing_address(self, address: Address):
        self._billing_address = address
        self._update_timestamp()
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    @property
    def notes(self) -> str:
        return self._notes
    
    @notes.setter
    def notes(self, value: str):
        self._notes = value
        self._update_timestamp()
    
    # ---------- Business Methods ----------
    def add_item(self, product: Product, quantity: int) -> None:
        """Add item to order with validation"""
        if not product.can_fulfill_order(quantity):
            raise ValueError(f"Product {product.name} cannot fulfill order for {quantity} units")
        
        if product.id in self._items:
            self._items[product.id].increase_quantity(quantity)
        else:
            order_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                unit_price=product.selling_price,
                quantity=quantity
            )
            self._items[product.id] = order_item
        
        self._update_timestamp()
    
    def remove_item(self, product_id: str) -> bool:
        """Remove item from order"""
        if product_id in self._items:
            del self._items[product_id]
            self._update_timestamp()
            return True
        return False
    
    def update_item_quantity(self, product_id: str, new_quantity: int) -> bool:
        """Update item quantity"""
        if product_id in self._items:
            if new_quantity <= 0:
                return self.remove_item(product_id)
            
            self._items[product_id].quantity = new_quantity
            self._items[product_id].total_price = self._items[product_id].calculate_total()
            self._update_timestamp()
            return True
        return False
    
    def get_items(self) -> List[OrderItem]:
        """Get all order items"""
        return list(self._items.values())
    
    def get_item_count(self) -> int:
        """Get total number of items in order"""
        return sum(item.quantity for item in self._items.values())
    
    def calculate_subtotal(self) -> Money:
        """Calculate order subtotal (sum of all items)"""
        subtotal = Money(Decimal('0'))
        for item in self._items.values():
            subtotal = subtotal + item.calculate_total()
        return subtotal
    
    def calculate_tax(self, tax_rate: Decimal = Decimal('0.1')) -> Money:
        """Calculate tax amount"""
        if not 0 <= tax_rate <= 1:
            raise ValueError("Tax rate must be between 0 and 1")
        subtotal = self.calculate_subtotal()
        return Money(subtotal.amount * tax_rate)
    
    def calculate_shipping_cost(self, base_cost: Money = Money(Decimal('10'))) -> Money:
        """Calculate shipping cost"""
        item_count = self.get_item_count()
        if item_count == 0:
            return Money(Decimal('0'))
        # Simple shipping calculation: base cost + $1 per item
        return base_cost + Money(Decimal('1') * item_count)
    
    def calculate_discount(self, discount_percentage: Decimal) -> Money:
        """Calculate discount amount"""
        if not 0 <= discount_percentage <= 100:
            raise ValueError("Discount percentage must be between 0 and 100")
        subtotal = self.calculate_subtotal()
        discount_amount = subtotal.amount * (discount_percentage / Decimal('100'))
        return Money(discount_amount)
    
    def calculate_total(self, 
                       tax_rate: Decimal = Decimal('0.1'),
                       shipping_cost: Money = None,
                       discount_percentage: Decimal = Decimal('0')) -> Money:
        """Calculate order total with tax, shipping, and discount"""
        subtotal = self.calculate_subtotal()
        
        # Calculate tax
        tax = self.calculate_tax(tax_rate)
        
        # Calculate shipping
        shipping = shipping_cost or self.calculate_shipping_cost()
        
        # Calculate discount
        discount = self.calculate_discount(discount_percentage)
        
        # Calculate total
        total_amount = subtotal.amount + tax.amount + shipping.amount - discount.amount
        
        # Ensure total is not negative
        if total_amount < 0:
            total_amount = Decimal('0')
        
        return Money(total_amount)
    
    def change_status(self, new_status: OrderStatus) -> None:
        """Change order status with validation"""
        if not OrderStatus.can_transition(self._status, new_status):
            raise ValueError(
                f"Cannot change status from {self._status.value} to {new_status.value}"
            )
        self._status = new_status
        self._update_timestamp()
    
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled"""
        return self._status in [OrderStatus.DRAFT, OrderStatus.PENDING, 
                               OrderStatus.CONFIRMED, OrderStatus.PROCESSING]
    
    def can_be_modified(self) -> bool:
        """Check if order can be modified"""
        return self._status in [OrderStatus.DRAFT, OrderStatus.PENDING]
    
    def is_completed(self) -> bool:
        """Check if order is completed"""
        return self._status in [OrderStatus.DELIVERED, OrderStatus.REFUNDED]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get order summary for presentation"""
        return {
            'id': self.id,
            'customer_name': self._customer_name,
            'customer_email': self._customer_email,
            'shipping_address': str(self._shipping_address) if self._shipping_address else None,
            'billing_address': str(self._billing_address) if self._billing_address else None,
            'status': self._status.value,
            'item_count': self.get_item_count(),
            'subtotal': str(self.calculate_subtotal()),
            'total': str(self.calculate_total()),
            'notes': self._notes,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
    
    def get_detailed_summary(self) -> Dict[str, Any]:
        """Get detailed order summary with items"""
        summary = self.get_summary()
        summary['items'] = [item.to_dict() for item in self.get_items()]
        summary['item_details'] = [
            f"{item.product_name} x{item.quantity} @ {item.unit_price}"
            for item in self.get_items()
        ]
        return summary
    
    def __str__(self) -> str:
        return f"Order #{self.id} - {self._customer_name} - {self._status.value} - Total: {self.calculate_total()}"

# ---------- Employee Entity ----------
class Employee(Entity):
    """Employee domain entity with role-based permissions"""
    
    MIN_SALARY = Decimal('10000')
    MAX_SALARY = Decimal('1000000')
    
    def __init__(self,
                 id: str,
                 name: str,
                 email: str,
                 role: EmployeeRole,
                 salary: Money,
                 hire_date: date = None,
                 phone: str = "",
                 department: str = "",
                 manager_id: str = None):
        super().__init__(id)
        self._name = name
        self._email = email
        self._role = role
        self._salary = salary
        self._hire_date = hire_date or date.today()
        self._phone = phone
        self._department = department
        self._manager_id = manager_id
        self._assigned_tasks: List[str] = []
        self._performance_rating: Decimal = Decimal('0')
        
        self._validate()
    
    def _validate(self):
        """Validate employee business rules"""
        if not self._name or len(self._name) < 2:
            raise ValueError("Employee name must be at least 2 characters")
        
        if '@' not in self._email:
            raise ValueError("Invalid email address")
        
        if self._salary.amount < self.MIN_SALARY:
            raise ValueError(f"Salary must be at least {self.MIN_SALARY}")
        
        if self._salary.amount > self.MAX_SALARY:
            raise ValueError(f"Salary cannot exceed {self.MAX_SALARY}")
    
    # ---------- Properties ----------
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        if len(value) < 2:
            raise ValueError("Employee name must be at least 2 characters")
        self._name = value
        self._update_timestamp()
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str):
        if '@' not in value:
            raise ValueError("Invalid email address")
        self._email = value
        self._update_timestamp()
    
    @property
    def role(self) -> EmployeeRole:
        return self._role
    
    @role.setter
    def role(self, value: EmployeeRole):
        self._role = value
        self._update_timestamp()
    
    @property
    def salary(self) -> Money:
        return self._salary
    
    @salary.setter
    def salary(self, value: Money):
        if value.amount < self.MIN_SALARY:
            raise ValueError(f"Salary must be at least {self.MIN_SALARY}")
        if value.amount > self.MAX_SALARY:
            raise ValueError(f"Salary cannot exceed {self.MAX_SALARY}")
        self._salary = value
        self._update_timestamp()
    
    @property
    def hire_date(self) -> date:
        return self._hire_date
    
    @property
    def phone(self) -> str:
        return self._phone
    
    @phone.setter
    def phone(self, value: str):
        self._phone = value
        self._update_timestamp()
    
    @property
    def department(self) -> str:
        return self._department
    
    @department.setter
    def department(self, value: str):
        self._department = value
        self._update_timestamp()
    
    @property
    def manager_id(self) -> Optional[str]:
        return self._manager_id
    
    @manager_id.setter
    def manager_id(self, value: Optional[str]):
        self._manager_id = value
        self._update_timestamp()
    
    @property
    def performance_rating(self) -> Decimal:
        return self._performance_rating
    
    @performance_rating.setter
    def performance_rating(self, value: Decimal):
        if not 0 <= value <= 5:
            raise ValueError("Performance rating must be between 0 and 5")
        self._performance_rating = value
        self._update_timestamp()
    
    # ---------- Business Methods ----------
    def calculate_years_of_service(self) -> int:
        """Calculate years of service"""
        today = date.today()
        years = today.year - self._hire_date.year
        
        if (today.month, today.day) < (self._hire_date.month, self._hire_date.day):
            years -= 1
        
        return years
    
    def assign_task(self, task: str) -> None:
        """Assign a task to employee"""
        if task not in self._assigned_tasks:
            self._assigned_tasks.append(task)
            self._update_timestamp()
    
    def remove_task(self, task: str) -> bool:
        """Remove task from employee"""
        if task in self._assigned_tasks:
            self._assigned_tasks.remove(task)
            self._update_timestamp()
            return True
        return False
    
    def get_tasks(self) -> List[str]:
        """Get all assigned tasks"""
        return self._assigned_tasks.copy()
    
    def has_permission(self, permission: str) -> bool:
        """Check if employee has specific permission"""
        return permission in self._role.get_permissions()
    
    def can_manage(self, other: 'Employee') -> bool:
        """Check if this employee can manage another employee"""
        if self._role == EmployeeRole.MANAGER or self._role == EmployeeRole.ADMIN:
            return other._role != EmployeeRole.ACCOUNTANT  # Manager/Admin cannot manage Accountant
        if self._role == EmployeeRole.SUPERVISOR and other._role not in [
            EmployeeRole.MANAGER, EmployeeRole.ADMIN, EmployeeRole.ACCOUNTANT
        ]:
            return True
        return False
    
    def calculate_bonus(self, bonus_percentage: Decimal = Decimal('0.1')) -> Money:
        """Calculate performance bonus"""
        if not 0 <= bonus_percentage <= 1:
            raise ValueError("Bonus percentage must be between 0 and 1")
        
        base_bonus = self._salary.amount * bonus_percentage
        performance_multiplier = Decimal('1') + (self._performance_rating / Decimal('10'))
        total_bonus = base_bonus * performance_multiplier
        
        return Money(total_bonus)
    
    def get_info(self) -> Dict[str, Any]:
        """Get employee information for presentation"""
        return {
            'id': self.id,
            'name': self._name,
            'email': self._email,
            'role': self._role.value,
            'salary': str(self._salary),
            'hire_date': self._hire_date.isoformat(),
            'years_of_service': self.calculate_years_of_service(),
            'phone': self._phone,
            'department': self._department,
            'manager_id': self._manager_id,
            'task_count': len(self._assigned_tasks),
            'performance_rating': str(self._performance_rating),
            'permissions': list(self._role.get_permissions()),
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
    
    def __str__(self) -> str:
        return f"Employee: {self._name} ({self._role.value}) - Dept: {self._department}"

# ==================== REPOSITORY PATTERN ====================

class Repository(ABC):
    """Repository Pattern: Interface for data access"""
    
    @abstractmethod
    def save(self, entity: Entity) -> None:
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[Entity]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Entity]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        pass

class ProductRepository(Repository):
    """Product repository interface"""
    
    @abstractmethod
    def search_by_name(self, name: str) -> List[Product]:
        pass
    
    @abstractmethod
    def get_by_category(self, category: ProductCategory) -> List[Product]:
        pass
    
    @abstractmethod
    def get_low_stock_products(self) -> List[Product]:
        pass
    
    @abstractmethod
    def get_by_price_range(self, min_price: Decimal, max_price: Decimal) -> List[Product]:
        pass

class OrderRepository(Repository):
    """Order repository interface"""
    
    @abstractmethod
    def get_by_status(self, status: OrderStatus) -> List[Order]:
        pass
    
    @abstractmethod
    def get_by_customer(self, customer_email: str) -> List[Order]:
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Order]:
        pass

class EmployeeRepository(Repository):
    """Employee repository interface"""
    
    @abstractmethod
    def get_by_role(self, role: EmployeeRole) -> List[Employee]:
        pass
    
    @abstractmethod
    def get_by_department(self, department: str) -> List[Employee]:
        pass
    
    @abstractmethod
    def get_managers(self) -> List[Employee]:
        pass

# ==================== INFRASTRUCTURE LAYER ====================

# ---------- SQLite Implementations ----------
class SQLiteProductRepository(ProductRepository):
    """SQLite implementation of product repository"""
    
    def __init__(self, db_path: str = "warehouse.db"):
        self.db_path = db_path
        self.db = DatabaseConnection.get_instance()
    
    def save(self, product: Product) -> None:
        """Save product to database"""
        details = product.get_details()
        
        # Serialize dimensions
        dimensions_json = json.dumps({k: str(v) for k, v in product.dimensions.items()})
        
        # Check if product exists
        self.db.execute_query("SELECT id FROM products WHERE id = ?", (product.id,))
        exists = self.db.cursor.fetchone()
        
        if exists:
            # Update existing product
            self.db.execute_query("""
                UPDATE products 
                SET name = ?, category = ?, purchase_price = ?, 
                    selling_price = ?, quantity = ?, sku = ?, 
                    attributes = ?, updated_at = ?
                WHERE id = ?
            """, (
                product.name,
                product.category.value,
                float(product.purchase_price.amount),
                float(product.selling_price.amount),
                product.quantity,
                product.sku,
                json.dumps({
                    'description': product.description,
                    'weight': str(product.weight),
                    'dimensions': dimensions_json
                }),
                product.updated_at.isoformat(),
                product.id
            ))
        else:
            # Insert new product
            self.db.execute_query("""
                INSERT INTO products 
                (id, name, category, purchase_price, selling_price, 
                 quantity, sku, attributes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.id,
                product.name,
                product.category.value,
                float(product.purchase_price.amount),
                float(product.selling_price.amount),
                product.quantity,
                product.sku,
                json.dumps({
                    'description': product.description,
                    'weight': str(product.weight),
                    'dimensions': dimensions_json
                }),
                product.created_at.isoformat(),
                product.updated_at.isoformat()
            ))
        
        self.db.commit()
    
    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        self.db.execute_query("SELECT * FROM products WHERE id = ?", (product_id,))
        row = self.db.cursor.fetchone()
        
        if row:
            return self._row_to_product(row)
        return None
    
    def get_all(self) -> List[Product]:
        """Get all products"""
        self.db.execute_query("SELECT * FROM products ORDER BY name")
        rows = self.db.cursor.fetchall()
        return [self._row_to_product(row) for row in rows]
    
    def delete(self, product_id: str) -> bool:
        """Delete product by ID"""
        self.db.execute_query("DELETE FROM products WHERE id = ?", (product_id,))
        self.db.commit()
        return self.db.cursor.rowcount > 0
    
    def search_by_name(self, name: str) -> List[Product]:
        """Search products by name"""
        self.db.execute_query(
            "SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)", 
            (f'%{name}%',)
        )
        rows = self.db.cursor.fetchall()
        return [self._row_to_product(row) for row in rows]
    
    def get_by_category(self, category: ProductCategory) -> List[Product]:
        """Get products by category"""
        self.db.execute_query(
            "SELECT * FROM products WHERE category = ?", 
            (category.value,)
        )
        rows = self.db.cursor.fetchall()
        return [self._row_to_product(row) for row in rows]
    
    def get_low_stock_products(self) -> List[Product]:
        """Get products with low stock"""
        all_products = self.get_all()
        return [p for p in all_products if p.is_low_stock()]
    
    def get_by_price_range(self, min_price: Decimal, max_price: Decimal) -> List[Product]:
        """Get products by price range"""
        self.db.execute_query(
            "SELECT * FROM products WHERE selling_price BETWEEN ? AND ?",
            (float(min_price), float(max_price))
        )
        rows = self.db.cursor.fetchall()
        return [self._row_to_product(row) for row in rows]
    
    def _row_to_product(self, row) -> Product:
        """Convert database row to Product entity"""
        # Parse attributes JSON
        attributes = json.loads(row[7]) if row[7] else {}
        
        # Create appropriate product type based on category
        category = ProductCategory(row[2])
        
        if category == ProductCategory.CLOTHING:
            product = ClothingProduct(
                id=row[0],
                name=row[1],
                category=category,
                purchase_price=Money(Decimal(str(row[3]))),
                selling_price=Money(Decimal(str(row[4]))),
                quantity=row[5],
                sku=row[6],
                description=attributes.get('description', '')
            )
        elif category == ProductCategory.FOOD:
            product = FoodProduct(
                id=row[0],
                name=row[1],
                category=category,
                purchase_price=Money(Decimal(str(row[3]))),
                selling_price=Money(Decimal(str(row[4]))),
                quantity=row[5],
                sku=row[6],
                description=attributes.get('description', '')
            )
        elif category == ProductCategory.BOOKS:
            product = BookProduct(
                id=row[0],
                name=row[1],
                category=category,
                purchase_price=Money(Decimal(str(row[3]))),
                selling_price=Money(Decimal(str(row[4]))),
                quantity=row[5],
                sku=row[6],
                description=attributes.get('description', '')
            )
        else:
            product = Product(
                id=row[0],
                name=row[1],
                category=category,
                purchase_price=Money(Decimal(str(row[3]))),
                selling_price=Money(Decimal(str(row[4]))),
                quantity=row[5],
                sku=row[6],
                description=attributes.get('description', ''),
                weight=Decimal(attributes.get('weight', '0')),
                dimensions={k: Decimal(v) for k, v in json.loads(attributes.get('dimensions', '{}')).items()}
            )
        
        # Set internal datetime attributes
        product._created_at = datetime.fromisoformat(row[8])
        product._updated_at = datetime.fromisoformat(row[9])
        
        return product

# ---------- CSV Repository (Alternative Implementation) ----------
class CSVProductRepository(ProductRepository):
    """CSV implementation of product repository"""
    
    def __init__(self, filename: str = "products.csv"):
        self.filename = filename
        self._products: Dict[str, Product] = {}
        self._load_from_csv()
    
    def _load_from_csv(self):
        """Load products from CSV file"""
        if not os.path.exists(self.filename):
            # Create empty file with headers
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'id', 'name', 'category', 'purchase_price', 
                    'selling_price', 'quantity', 'sku', 'description'
                ])
            return
        
        with open(self.filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    category = ProductCategory(row['category'])
                    product = Product(
                        id=row['id'],
                        name=row['name'],
                        category=category,
                        purchase_price=Money(Decimal(row['purchase_price'])),
                        selling_price=Money(Decimal(row['selling_price'])),
                        quantity=int(row['quantity']),
                        sku=row['sku'],
                        description=row.get('description', '')
                    )
                    self._products[product.id] = product
                except Exception as e:
                    print(f"Warning: Could not load product {row.get('id', 'unknown')}: {e}")
    
    def _save_to_csv(self):
        """Save products to CSV file"""
        with open(self.filename, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['id', 'name', 'category', 'purchase_price', 
                         'selling_price', 'quantity', 'sku', 'description']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for product in self._products.values():
                writer.writerow({
                    'id': product.id,
                    'name': product.name,
                    'category': product.category.value,
                    'purchase_price': str(product.purchase_price.amount),
                    'selling_price': str(product.selling_price.amount),
                    'quantity': product.quantity,
                    'sku': product.sku,
                    'description': product.description
                })
    
    def save(self, product: Product) -> None:
        self._products[product.id] = product
        self._save_to_csv()
    
    def get_by_id(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)
    
    def get_all(self) -> List[Product]:
        return list(self._products.values())
    
    def delete(self, product_id: str) -> bool:
        if product_id in self._products:
            del self._products[product_id]
            self._save_to_csv()
            return True
        return False
    
    def search_by_name(self, name: str) -> List[Product]:
        name_lower = name.lower()
        return [p for p in self._products.values() if name_lower in p.name.lower()]
    
    def get_by_category(self, category: ProductCategory) -> List[Product]:
        return [p for p in self._products.values() if p.category == category]
    
    def get_low_stock_products(self) -> List[Product]:
        return [p for p in self._products.values() if p.is_low_stock()]
    
    def get_by_price_range(self, min_price: Decimal, max_price: Decimal) -> List[Product]:
        return [p for p in self._products.values() 
                if min_price <= p.selling_price.amount <= max_price]

# ==================== USE CASES LAYER ====================

class UseCase(ABC):
    """Base class for all use cases"""
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the use case"""
        pass

# ---------- Product Management ----------
class ProductManagementUseCase(UseCase):
    """Use cases for product management"""
    
    def __init__(self, product_repository: ProductRepository):
        self._product_repository = product_repository
    
    def create_product(self, 
                      name: str,
                      category: ProductCategory,
                      purchase_price: Decimal,
                      selling_price: Decimal,
                      quantity: int,
                      description: str = "") -> Product:
        """Create new product"""
        product_id = str(uuid.uuid4())
        product = Product(
            id=product_id,
            name=name,
            category=category,
            purchase_price=Money(purchase_price),
            selling_price=Money(selling_price),
            quantity=quantity,
            description=description
        )
        
        self._product_repository.save(product)
        return product
    
    def update_product_price(self, product_id: str, new_price: Decimal) -> Product:
        """Update product selling price"""
        product = self._product_repository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        product.selling_price = Money(new_price)
        self._product_repository.save(product)
        return product
    
    def restock_product(self, product_id: str, quantity: int) -> Product:
        """Restock product quantity"""
        product = self._product_repository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        product.increase_quantity(quantity)
        self._product_repository.save(product)
        return product
    
    def get_low_stock_products(self) -> List[Product]:
        """Get all products with low stock"""
        return self._product_repository.get_low_stock_products()
    
    def calculate_inventory_value(self) -> Money:
        """Calculate total inventory value"""
        all_products = self._product_repository.get_all()
        total = Money(Decimal('0'))
        for product in all_products:
            total = total + product.calculate_total_value()
        return total
    
    def search_products(self, query: str) -> List[Product]:
        """Search products by name"""
        return self._product_repository.search_by_name(query)
    
    def get_products_by_category(self, category: ProductCategory) -> List[Product]:
        """Get products by category"""
        return self._product_repository.get_by_category(category)

# ---------- Order Management ----------
class OrderManagementUseCase(UseCase):
    """Use cases for order management"""
    
    def __init__(self, 
                 order_repository: OrderRepository,
                 product_repository: ProductRepository):
        self._order_repository = order_repository
        self._product_repository = product_repository
    
    def create_order(self, 
                    customer_name: str, 
                    customer_email: str,
                    shipping_address: Address = None) -> Order:
        """Create new order"""
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        order = Order(
            id=order_id,
            customer_name=customer_name,
            customer_email=customer_email,
            shipping_address=shipping_address
        )
        
        self._order_repository.save(order)
        return order
    
    def add_product_to_order(self, order_id: str, product_id: str, quantity: int) -> Order:
        """Add product to existing order"""
        order = self._order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        product = self._product_repository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        order.add_item(product, quantity)
        self._order_repository.save(order)
        return order
    
    def process_order(self, order_id: str) -> Order:
        """Process order and update inventory"""
        order = self._order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Check if all items are available
        for item in order.get_items():
            product = self._product_repository.get_by_id(item.product_id)
            if not product or not product.can_fulfill_order(item.quantity):
                raise ValueError(f"Cannot fulfill order for product {item.product_name}")
        
        # Update product quantities
        for item in order.get_items():
            product = self._product_repository.get_by_id(item.product_id)
            product.decrease_quantity(item.quantity)
            self._product_repository.save(product)
        
        order.change_status(OrderStatus.PROCESSING)
        self._order_repository.save(order)
        return order
    
    def complete_order(self, order_id: str) -> Order:
        """Mark order as completed"""
        order = self._order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        order.change_status(OrderStatus.DELIVERED)
        self._order_repository.save(order)
        return order
    
    def cancel_order(self, order_id: str) -> Order:
        """Cancel order and restore inventory"""
        order = self._order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if not order.can_be_cancelled():
            raise ValueError(f"Order {order_id} cannot be cancelled")
        
        # Restore product quantities if order was processing
        if order.status == OrderStatus.PROCESSING:
            for item in order.get_items():
                product = self._product_repository.get_by_id(item.product_id)
                if product:
                    product.increase_quantity(item.quantity)
                    self._product_repository.save(product)
        
        order.change_status(OrderStatus.CANCELLED)
        self._order_repository.save(order)
        return order
    
    def calculate_order_statistics(self, 
                                 start_date: date = None, 
                                 end_date: date = None) -> Dict[str, Any]:
        """Calculate order statistics for date range"""
        all_orders = self._order_repository.get_all()
        
        # Filter by date range if provided
        if start_date and end_date:
            filtered_orders = [
                o for o in all_orders 
                if start_date <= o.created_at.date() <= end_date
            ]
        else:
            filtered_orders = all_orders
        
        total_orders = len(filtered_orders)
        pending_orders = len([o for o in filtered_orders if o.status == OrderStatus.PENDING])
        processing_orders = len([o for o in filtered_orders if o.status == OrderStatus.PROCESSING])
        completed_orders = len([o for o in filtered_orders if o.is_completed()])
        cancelled_orders = len([o for o in filtered_orders if o.status == OrderStatus.CANCELLED])
        
        total_revenue = Money(Decimal('0'))
        total_items = 0
        
        for order in filtered_orders:
            if order.is_completed():
                total_revenue = total_revenue + order.calculate_total()
                total_items += order.get_item_count()
        
        avg_order_value = Money(Decimal('0'))
        if completed_orders > 0:
            avg_amount = total_revenue.amount / completed_orders
            avg_order_value = Money(avg_amount)
        
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': str(total_revenue),
            'total_items_sold': total_items,
            'average_order_value': str(avg_order_value),
            'completion_rate': f"{(completed_orders/total_orders*100):.1f}%" if total_orders > 0 else "0%",
            'cancellation_rate': f"{(cancelled_orders/total_orders*100):.1f}%" if total_orders > 0 else "0%"
        }

# ---------- Employee Management ----------
class EmployeeManagementUseCase(UseCase):
    """Use cases for employee management"""
    
    def __init__(self, employee_repository: EmployeeRepository):
        self._employee_repository = employee_repository
    
    def hire_employee(self,
                     name: str,
                     email: str,
                     role: EmployeeRole,
                     salary: Decimal,
                     department: str = "",
                     phone: str = "") -> Employee:
        """Hire new employee"""
        employee_id = f"EMP-{uuid.uuid4().hex[:6].upper()}"
        employee = Employee(
            id=employee_id,
            name=name,
            email=email,
            role=role,
            salary=Money(salary),
            department=department,
            phone=phone
        )
        
        self._employee_repository.save(employee)
        return employee
    
    def promote_employee(self, employee_id: str, new_role: EmployeeRole) -> Employee:
        """Promote employee to new role"""
        employee = self._employee_repository.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        employee.role = new_role
        self._employee_repository.save(employee)
        return employee
    
    def update_employee_salary(self, employee_id: str, new_salary: Decimal) -> Employee:
        """Update employee salary"""
        employee = self._employee_repository.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        employee.salary = Money(new_salary)
        self._employee_repository.save(employee)
        return employee
    
    def assign_task_to_employee(self, employee_id: str, task: str) -> Employee:
        """Assign task to employee"""
        employee = self._employee_repository.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        employee.assign_task(task)
        self._employee_repository.save(employee)
        return employee
    
    def calculate_payroll(self) -> Dict[str, Any]:
        """Calculate payroll for all employees"""
        all_employees = self._employee_repository.get_all()
        
        total_monthly_salary = Money(Decimal('0'))
        total_yearly_salary = Money(Decimal('0'))
        department_costs = {}
        role_counts = {}
        
        for employee in all_employees:
            total_monthly_salary = total_monthly_salary + employee.salary
            
            # Accumulate department costs
            department = employee.department or "Unassigned"
            if department not in department_costs:
                department_costs[department] = Money(Decimal('0'))
            department_costs[department] = department_costs[department] + employee.salary
            
            # Count roles
            role = employee.role.value
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Calculate yearly salary (12 months)
        total_yearly_salary = Money(total_monthly_salary.amount * 12)
        
        # Calculate average salary
        avg_monthly_salary = Money(Decimal('0'))
        if all_employees:
            avg_amount = total_monthly_salary.amount / len(all_employees)
            avg_monthly_salary = Money(avg_amount)
        
        return {
            'employee_count': len(all_employees),
            'total_monthly_salary': str(total_monthly_salary),
            'total_yearly_salary': str(total_yearly_salary),
            'average_monthly_salary': str(avg_monthly_salary),
            'department_costs': {dept: str(cost) for dept, cost in department_costs.items()},
            'role_distribution': role_counts
        }

# ---------- Report Generation ----------
class ReportGenerationUseCase(UseCase):
    """Use cases for report generation"""
    
    def __init__(self,
                 product_repository: ProductRepository,
                 order_repository: OrderRepository,
                 employee_repository: EmployeeRepository):
        self._product_repository = product_repository
        self._order_repository = order_repository
        self._employee_repository = employee_repository
    
    def generate_inventory_report(self) -> Dict[str, Any]:
        """Generate comprehensive inventory report"""
        # Create inventory report generator
        report_generator = InventoryReportGenerator(self._product_repository)
        return report_generator.generate_report()
    
    def generate_sales_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate sales report for date range"""
        # Create sales report generator
        report_generator = SalesReportGenerator(self._order_repository)
        report = report_generator.generate_report()
        
        # Add date range information
        report['date_range'] = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': (end_date - start_date).days + 1
        }
        
        return report
    
    def generate_employee_performance_report(self) -> Dict[str, Any]:
        """Generate employee performance report"""
        all_employees = self._employee_repository.get_all()
        
        performance_summary = {}
        department_performance = {}
        
        for employee in all_employees:
            # Categorize performance
            rating = employee.performance_rating
            if rating >= Decimal('4.5'):
                category = "Excellent"
            elif rating >= Decimal('4.0'):
                category = "Very Good"
            elif rating >= Decimal('3.0'):
                category = "Good"
            elif rating >= Decimal('2.0'):
                category = "Needs Improvement"
            else:
                category = "Poor"
            
            # Update performance summary
            performance_summary[category] = performance_summary.get(category, 0) + 1
            
            # Update department performance
            department = employee.department or "Unassigned"
            if department not in department_performance:
                department_performance[department] = {
                    'total_rating': Decimal('0'),
                    'employee_count': 0,
                    'average_rating': Decimal('0')
                }
            
            dept_data = department_performance[department]
            dept_data['total_rating'] += rating
            dept_data['employee_count'] += 1
            dept_data['average_rating'] = dept_data['total_rating'] / dept_data['employee_count']
        
        # Calculate overall average rating
        total_rating = sum(emp.performance_rating for emp in all_employees)
        overall_average = total_rating / len(all_employees) if all_employees else Decimal('0')
        
        return {
            'total_employees': len(all_employees),
            'overall_average_rating': str(overall_average),
            'performance_summary': performance_summary,
            'department_performance': {
                dept: {
                    'average_rating': str(data['average_rating']),
                    'employee_count': data['employee_count']
                }
                for dept, data in department_performance.items()
            },
            'top_performers': sorted(
                [emp.get_info() for emp in all_employees],
                key=lambda x: Decimal(x['performance_rating']),
                reverse=True
            )[:5],
            'report_date': datetime.now().isoformat()
        }

# ==================== PRESENTATION LAYER ====================

class Presenter(ABC):
    """Base presenter for formatting output"""
    
    @abstractmethod
    def present(self, data: Any) -> Any:
        pass

class ProductPresenter(Presenter):
    """Presenter for product data"""
    
    def present(self, product: Product) -> Dict[str, Any]:
        return product.get_details()
    
    def present_list(self, products: List[Product]) -> List[Dict[str, Any]]:
        return [self.present(p) for p in products]
    
    def present_summary(self, products: List[Product]) -> Dict[str, Any]:
        """Present product summary"""
        total_value = Money(Decimal('0'))
        low_stock_count = 0
        categories = {}
        
        for product in products:
            total_value = total_value + product.calculate_total_value()
            if product.is_low_stock():
                low_stock_count += 1
            
            category = product.category.value
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_products': len(products),
            'total_inventory_value': str(total_value),
            'low_stock_count': low_stock_count,
            'categories': categories
        }

class OrderPresenter(Presenter):
    """Presenter for order data"""
    
    def present(self, order: Order) -> Dict[str, Any]:
        return order.get_detailed_summary()
    
    def present_list(self, orders: List[Order]) -> List[Dict[str, Any]]:
        return [self.present(o) for o in orders]
    
    def present_statistics(self, statistics: Dict[str, Any]) -> Dict[str, Any]:
        """Present order statistics in a formatted way"""
        return {
            'summary': {
                'total_orders': statistics.get('total_orders', 0),
                'total_revenue': statistics.get('total_revenue', 'USD 0.00'),
                'completion_rate': statistics.get('completion_rate', '0%')
            },
            'status_breakdown': {
                'pending': statistics.get('pending_orders', 0),
                'processing': statistics.get('processing_orders', 0),
                'completed': statistics.get('completed_orders', 0),
                'cancelled': statistics.get('cancelled_orders', 0)
            },
            'performance_metrics': {
                'average_order_value': statistics.get('average_order_value', 'USD 0.00'),
                'total_items_sold': statistics.get('total_items_sold', 0),
                'cancellation_rate': statistics.get('cancellation_rate', '0%')
            }
        }

class EmployeePresenter(Presenter):
    """Presenter for employee data"""
    
    def present(self, employee: Employee) -> Dict[str, Any]:
        return employee.get_info()
    
    def present_list(self, employees: List[Employee]) -> List[Dict[str, Any]]:
        return [self.present(e) for e in employees]
    
    def present_payroll_summary(self, payroll_data: Dict[str, Any]) -> Dict[str, Any]:
        """Present payroll summary"""
        return {
            'financial_summary': {
                'total_employees': payroll_data.get('employee_count', 0),
                'monthly_payroll': payroll_data.get('total_monthly_salary', 'USD 0.00'),
                'yearly_payroll': payroll_data.get('total_yearly_salary', 'USD 0.00'),
                'average_salary': payroll_data.get('average_monthly_salary', 'USD 0.00')
            },
            'department_costs': payroll_data.get('department_costs', {}),
            'role_distribution': payroll_data.get('role_distribution', {})
        }

class ReportPresenter(Presenter):
    """Presenter for report data"""
    
    def present(self, report_data: Dict[str, Any]) -> str:
        """Format report as string for display"""
        report_type = report_data.get('report_type', 'Unknown Report')
        generated_at = report_data.get('generated_at', 'Unknown date')
        data = report_data.get('data', {})
        
        lines = []
        lines.append("=" * 70)
        lines.append(f"REPORT: {report_type}")
        lines.append(f"Generated: {generated_at}")
        lines.append("=" * 70)
        lines.append("")
        
        # Format the data
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    lines.append(f"{key.upper().replace('_', ' ')}:")
                    for sub_key, sub_value in value.items():
                        lines.append(f"  {sub_key}: {sub_value}")
                    lines.append("")
                elif isinstance(value, list):
                    lines.append(f"{key.upper().replace('_', ' ')} ({len(value)} items):")
                    for item in value[:10]:  # Limit to first 10 items
                        if isinstance(item, dict):
                            lines.append(f"  - {item}")
                        else:
                            lines.append(f"  - {item}")
                    if len(value) > 10:
                        lines.append(f"  ... and {len(value) - 10} more items")
                    lines.append("")
                else:
                    lines.append(f"{key.upper().replace('_', ' ')}: {value}")
        else:
            lines.append(str(data))
        
        lines.append("=" * 70)
        return "\n".join(lines)

# ==================== APPLICATION CONFIGURATION ====================

class ApplicationConfig:
    """Application configuration and dependency injection"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize application configuration"""
        # Choose repository implementation
        self.use_sqlite = True  # Change to False to use CSV
        self.db_path = "warehouse.db"
        
        # Initialize repositories
        if self.use_sqlite:
            # Initialize database connection
            self.db = DatabaseConnection(self.db_path)
            
            # Create repositories
            self.product_repository = SQLiteProductRepository(self.db_path)
            
            # Note: Order and Employee repositories would be implemented similarly
            # For brevity, we'll use in-memory storage for these
            
            # Initialize in-memory repositories for now
            self._orders: Dict[str, Order] = {}
            self._employees: Dict[str, Employee] = {}
        else:
            self.product_repository = CSVProductRepository("products.csv")
            self._orders = {}
            self._employees = {}
        
        # Initialize use cases
        self.product_management = ProductManagementUseCase(self.product_repository)
        
        # Initialize presenters
        self.product_presenter = ProductPresenter()
        self.order_presenter = OrderPresenter()
        self.employee_presenter = EmployeePresenter()
        self.report_presenter = ReportPresenter()
        
        # Initialize observers
        self.email_notifier = EmailNotifier("admin@warehouse.com")
        self.log_notifier = LogNotifier("inventory_alerts.log")
        
        print(f"✅ Application initialized with {'SQLite' if self.use_sqlite else 'CSV'} storage")
    
    def get_product_management(self) -> ProductManagementUseCase:
        return self.product_management
    
    def get_product_presenter(self) -> ProductPresenter:
        return self.product_presenter
    
    def add_sample_data(self):
        """Add sample data for demonstration"""
        print("\n📦 Adding sample data...")
        
        try:
            # Create sample products using Factory Pattern
            from datetime import timedelta
            
            laptop = ProductFactory.create_electronics(
                name="Gaming Laptop",
                purchase_price=Decimal('800'),
                selling_price=Decimal('1200'),
                quantity=15
            )
            
            tshirt = ProductFactory.create_clothing(
                name="Cotton T-Shirt",
                purchase_price=Decimal('5'),
                selling_price=Decimal('15'),
                quantity=100,
                size="L",
                color="Blue"
            )
            
            chocolate = ProductFactory.create_food(
                name="Dark Chocolate",
                purchase_price=Decimal('2'),
                selling_price=Decimal('4'),
                quantity=50,
                expiration_date=date.today() + timedelta(days=90)
            )
            
            # Attach observers to products
            laptop.attach_observer(self.email_notifier)
            laptop.attach_observer(self.log_notifier)
            tshirt.attach_observer(self.email_notifier)
            chocolate.attach_observer(self.email_notifier)
            
            # Save products
            self.product_repository.save(laptop)
            self.product_repository.save(tshirt)
            self.product_repository.save(chocolate)
            
            print("✅ Sample products created:")
            print(f"   - {laptop.name} (Qty: {laptop.quantity})")
            print(f"   - {tshirt.name} (Qty: {tshirt.quantity})")
            print(f"   - {chocolate.name} (Qty: {chocolate.quantity})")
            
        except Exception as e:
            print(f"⚠️ Error creating sample data: {e}")
    
    def demonstrate_design_patterns(self):
        """Demonstrate all design patterns in action"""
        print("\n🎭 DEMONSTRATING DESIGN PATTERNS")
        print("=" * 50)
        
        # 1. Strategy Pattern
        print("\n1. STRATEGY PATTERN - Pricing Strategies")
        print("-" * 40)
        
        product = self.product_repository.get_all()[0] if self.product_repository.get_all() else None
        if product:
            strategies = [
                RegularPricing(),
                BulkDiscountPricing(discount_rate=Decimal('0.15'), min_quantity=10),
                SeasonalPricing(seasonal_multiplier=Decimal('1.2'))
            ]
            
            for strategy in strategies:
                total = product.apply_pricing_strategy(strategy, 20)
                print(f"   {strategy.get_description()}")
                print(f"   20 x {product.name}: {total}")
        
        # 2. Factory Pattern
        print("\n2. FACTORY PATTERN - Product Creation")
        print("-" * 40)
        
        new_product = ProductFactory.create_electronics(
            name="Factory Created Product",
            purchase_price=Decimal('100'),
            selling_price=Decimal('150'),
            quantity=25
        )
        print(f"   Created: {new_product.name} (SKU: {new_product.sku})")
        
        # 3. Decorator Pattern
        print("\n3. DECORATOR PATTERN - Product Enhancement")
        print("-" * 40)
        
        if product:
            # Apply discount decorator
            discounted = DiscountedProduct(product, Decimal('20'))
            print(f"   Original: {product.selling_price}")
            print(f"   Discounted: {discounted.get_selling_price()} (20% off)")
            
            # Apply featured decorator
            featured = FeaturedProduct(product, "Best Seller", "gold")
            details = featured.get_details()
            print(f"   Featured: {details['feature_description']}")
        
        # 4. Observer Pattern
        print("\n4. OBSERVER PATTERN - Inventory Notifications")
        print("-" * 40)
        
        if product:
            # Simulate low stock
            product.decrease_quantity(product.quantity - 5)
            print(f"   {product.name} now has {product.quantity} units")
            print("   Observers notified automatically!")
        
        # 5. Singleton Pattern
        print("\n5. SINGLETON PATTERN - Database Connection")
        print("-" * 40)
        
        db1 = DatabaseConnection.get_instance()
        db2 = DatabaseConnection.get_instance()
        print(f"   Database instances are the same: {db1 is db2}")
        
        # 6. Template Method Pattern
        print("\n6. TEMPLATE METHOD PATTERN - Report Generation")
        print("-" * 40)
        
        report_gen = InventoryReportGenerator(self.product_repository)
        report = report_gen.generate_report()
        print(f"   Generated: {report['report_type']}")
        print(f"   Total products: {report['data'].get('total_products', 0)}")
        
        print("\n" + "=" * 50)
        print("✅ Design patterns demonstrated successfully!")

# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point"""
    
    print("=" * 70)
    print("WAREHOUSE MANAGEMENT SYSTEM - FINAL VERSION")
    print("OOP & VVRPO Course Project - 2024")
    print("=" * 70)
    
    try:
        # Initialize application
        config = ApplicationConfig()
        
        # Add sample data
        config.add_sample_data()
        
        # Demonstrate design patterns
        config.demonstrate_design_patterns()
        
        # Show main menu
        print("\n📋 MAIN MENU")
        print("1. View all products")
        print("2. View low stock products")
        print("3. Calculate inventory value")
        print("4. Demonstrate more patterns")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            # View all products
            products = config.product_repository.get_all()
            if products:
                print(f"\n📦 All Products ({len(products)} items):")
                for product in products:
                    print(f"   • {product.name} - {product.quantity} units - {product.selling_price}")
            else:
                print("\nNo products found.")
        
        elif choice == "2":
            # View low stock products
            low_stock = config.product_repository.get_low_stock_products()
            if low_stock:
                print(f"\n⚠️  Low Stock Products ({len(low_stock)} items):")
                for product in low_stock:
                    print(f"   • {product.name} - {product.quantity} units (Min: {Product.MIN_STOCK_LEVEL})")
            else:
                print("\nNo low stock products.")
        
        elif choice == "3":
            # Calculate inventory value
            total_value = Money(Decimal('0'))
            products = config.product_repository.get_all()
            
            for product in products:
                total_value = total_value + product.calculate_total_value()
            
            print(f"\n💰 Total Inventory Value: {total_value}")
            print(f"   Based on {len(products)} products")
        
        elif choice == "4":
            # Demonstrate more patterns
            print("\n🎯 Additional Pattern Demonstrations")
            
            # Create a product with decorators
            sample_product = Product(
                id="SAMPLE-001",
                name="Sample Product",
                category=ProductCategory.ELECTRONICS,
                purchase_price=Money(Decimal('50')),
                selling_price=Money(Decimal('80')),
                quantity=30
            )
            
            # Apply multiple decorators
            decorated = LimitedEditionProduct(
                FeaturedProduct(
                    DiscountedProduct(sample_product, Decimal('15')),
                    "Limited Time Offer",
                    "red"
                ),
                edition_number=42,
                total_edition=1000
            )
            
            details = decorated.get_details()
            print("\n🎁 Multi-decorated Product:")
            for key, value in details.items():
                if value:
                    print(f"   {key}: {value}")
        
        elif choice == "5":
            print("\n👋 Goodbye!")
        
        else:
            print("\n❌ Invalid choice.")
    
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n" + "=" * 70)
        print("Thank you for using Warehouse Management System!")
        print("=" * 70)

# ==================== UNIT TEST RUNNER ====================

def run_unit_tests():
    """Run unit tests for design patterns"""
    import unittest
    
    print("Running unit tests for design patterns...")
    
    # Create test suite
    test_loader = unittest.TestLoader()
    
    # Import test modules
    try:
        # Try to import test modules
        import sys
        sys.path.append('.')
        
        # Run tests
        test_suite = test_loader.discover(start_dir='.', pattern='test_*.py')
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(test_suite)
        
        if result.wasSuccessful():
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed.")
    
    except ImportError as e:
        print(f"⚠️ Could not run tests: {e}")
        print("Please ensure test files are in the current directory.")

# ==================== DOCKER SUPPORT ====================

def docker_main():
    """Entry point for Docker container"""
    import sys
    print("🚀 Starting Warehouse System in Docker container...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if database exists
    if os.path.exists("warehouse.db"):
        print("✅ Database file found")
    else:
        print("⚠️ Database file not found, will be created")
    
    # Run main application
    main()

# ==================== MODULE ENTRY POINT ====================

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            run_unit_tests()
        elif sys.argv[1] == "--docker":
            docker_main()
        elif sys.argv[1] == "--help":
            print("Usage: python warehouse_final.py [OPTION]")
            print("Options:")
            print("  --test     Run unit tests")
            print("  --docker   Run in Docker mode")
            print("  --help     Show this help message")
            print("  (no args)  Run main application")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information.")
    else:
        # Run main application
        main()