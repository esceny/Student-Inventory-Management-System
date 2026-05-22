"""
models.py
---------
Contains all the main classes (models) for the system.
Each class handles one "thing" in our app:
  - ProductManager  → CRUD for products
  - SupplierManager → CRUD for suppliers
  - SalesManager    → recording sales and generating reports

These classes use OOP principles:
  - Encapsulation: each class manages its own data and logic
  - Separation of concerns: product logic ≠ supplier logic ≠ sales logic
"""

from tabulate import tabulate
from colorama import Fore, Style


# ================================================================
# PRODUCT MANAGER
# ================================================================

class ProductManager:
    """
    Handles all product-related database operations.
    CRUD = Create, Read, Update, Delete
    """

    def __init__(self, db):
        """
        db: a Database instance (from database.py)
        We store it so every method can run queries.
        """
        self.db = db

    # ---- CREATE ------------------------------------------------

    def add_product(self, name, category, quantity, price, threshold, supplier_id=None):
        """
        Add a new product to the database.
        Uses parameterized queries (%s) to prevent SQL injection.
        """
        cursor = self.db.get_cursor()
        if not cursor:
            return False

        query = """
            INSERT INTO products (name, category, quantity, price, low_stock_threshold, supplier_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(query, (name, category, quantity, price, threshold, supplier_id))
            self.db.commit()
            print(Fore.GREEN + f"\n✓ Product '{name}' added successfully!" + Style.RESET_ALL)
            return True
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not add product: {e}" + Style.RESET_ALL)
            return False

    # ---- READ --------------------------------------------------

    def get_all_products(self):
        """
        Fetch all products. Also joins with the suppliers table
        so we can show the supplier name instead of just the ID.
        """
        cursor = self.db.get_cursor()
        if not cursor:
            return []

        query = """
            SELECT 
                p.id, p.name, p.category, p.quantity,
                p.price, p.low_stock_threshold,
                IFNULL(s.name, 'N/A') AS supplier
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            ORDER BY p.id
        """
        cursor.execute(query)
        return cursor.fetchall()

    def get_product_by_id(self, product_id):
        """Fetch a single product by its ID."""
        cursor = self.db.get_cursor()
        if not cursor:
            return None

        query = "SELECT * FROM products WHERE id = %s"
        cursor.execute(query, (product_id,))
        return cursor.fetchone()

    def search_products(self, keyword):
        """
        Search products by name or category.
        LIKE '%keyword%' finds partial matches (e.g., 'cable' finds 'USB Cable').
        """
        cursor = self.db.get_cursor()
        if not cursor:
            return []

        query = """
            SELECT 
                p.id, p.name, p.category, p.quantity,
                p.price, p.low_stock_threshold,
                IFNULL(s.name, 'N/A') AS supplier
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.name LIKE %s OR p.category LIKE %s
        """
        like_keyword = f"%{keyword}%"
        cursor.execute(query, (like_keyword, like_keyword))
        return cursor.fetchall()

    def get_low_stock_products(self):
        """
        Return products where quantity is at or below the low_stock_threshold.
        Useful to alert the user to reorder items.
        """
        cursor = self.db.get_cursor()
        if not cursor:
            return []

        query = """
            SELECT 
                p.id, p.name, p.category, p.quantity,
                p.low_stock_threshold,
                IFNULL(s.name, 'N/A') AS supplier
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.quantity <= p.low_stock_threshold
            ORDER BY p.quantity ASC
        """
        cursor.execute(query)
        return cursor.fetchall()

    # ---- UPDATE ------------------------------------------------

    def update_product(self, product_id, name, category, quantity, price, threshold):
        """Update an existing product's details."""
        cursor = self.db.get_cursor()
        if not cursor:
            return False

        query = """
            UPDATE products
            SET name=%s, category=%s, quantity=%s, price=%s, low_stock_threshold=%s
            WHERE id=%s
        """
        try:
            cursor.execute(query, (name, category, quantity, price, threshold, product_id))
            self.db.commit()
            print(Fore.GREEN + f"\n✓ Product ID {product_id} updated successfully!" + Style.RESET_ALL)
            return True
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not update product: {e}" + Style.RESET_ALL)
            return False

    # ---- DELETE ------------------------------------------------

    def delete_product(self, product_id):
        """Delete a product from the database by ID."""
        cursor = self.db.get_cursor()
        if not cursor:
            return False

        query = "DELETE FROM products WHERE id = %s"
        try:
            cursor.execute(query, (product_id,))
            self.db.commit()
            print(Fore.GREEN + f"\n✓ Product ID {product_id} deleted successfully!" + Style.RESET_ALL)
            return True
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not delete product: {e}" + Style.RESET_ALL)
            return False

    # ---- DISPLAY HELPERS ---------------------------------------

    def display_products(self, products):
        """
        Nicely print a list of products as a table using the tabulate library.
        tabulate formats lists of dicts into clean ASCII tables.
        """
        if not products:
            print(Fore.YELLOW + "\nNo products found." + Style.RESET_ALL)
            return

        # Pull out just the fields we want to show
        table_data = []
        for p in products:
            table_data.append([
                p["id"],
                p["name"],
                p["category"],
                p["quantity"],
                f"₹{p['price']:.2f}",
                p.get("supplier", "N/A")
            ])

        headers = ["ID", "Name", "Category", "Qty", "Price", "Supplier"]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    def display_low_stock(self, products):
        """Print low-stock products with a warning color."""
        if not products:
            print(Fore.GREEN + "\n✓ All products are well-stocked!" + Style.RESET_ALL)
            return

        print(Fore.RED + "\n⚠  LOW STOCK ALERT — These items need restocking:" + Style.RESET_ALL)
        table_data = []
        for p in products:
            table_data.append([
                p["id"],
                p["name"],
                p["category"],
                p["quantity"],      # current stock
                p["low_stock_threshold"],  # threshold
                p.get("supplier", "N/A")
            ])

        headers = ["ID", "Name", "Category", "Current Qty", "Min Threshold", "Supplier"]
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


# ================================================================
# SUPPLIER MANAGER
# ================================================================

class SupplierManager:
    """
    Handles all supplier-related database operations.
    Suppliers are vendors who provide products to the inventory.
    """

    def __init__(self, db):
        self.db = db

    def add_supplier(self, name, contact_person, phone, email, address):
        """Add a new supplier to the database."""
        cursor = self.db.get_cursor()
        if not cursor:
            return False

        query = """
            INSERT INTO suppliers (name, contact_person, phone, email, address)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(query, (name, contact_person, phone, email, address))
            self.db.commit()
            print(Fore.GREEN + f"\n✓ Supplier '{name}' added successfully!" + Style.RESET_ALL)
            return True
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not add supplier: {e}" + Style.RESET_ALL)
            return False

    def get_all_suppliers(self):
        """Fetch all suppliers from the database."""
        cursor = self.db.get_cursor()
        if not cursor:
            return []

        cursor.execute("SELECT * FROM suppliers ORDER BY id")
        return cursor.fetchall()

    def delete_supplier(self, supplier_id):
        """Delete a supplier. Products linked to them will have supplier set to NULL."""
        cursor = self.db.get_cursor()
        if not cursor:
            return False

        query = "DELETE FROM suppliers WHERE id = %s"
        try:
            cursor.execute(query, (supplier_id,))
            self.db.commit()
            print(Fore.GREEN + f"\n✓ Supplier ID {supplier_id} deleted." + Style.RESET_ALL)
            return True
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not delete supplier: {e}" + Style.RESET_ALL)
            return False

    def display_suppliers(self, suppliers):
        """Print suppliers as a formatted table."""
        if not suppliers:
            print(Fore.YELLOW + "\nNo suppliers found." + Style.RESET_ALL)
            return

        table_data = [
            [s["id"], s["name"], s["contact_person"], s["phone"], s["email"]]
            for s in suppliers
        ]
        headers = ["ID", "Company", "Contact Person", "Phone", "Email"]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


# ================================================================
# SALES MANAGER
# ================================================================

class SalesManager:
    """
    Handles recording sales and generating sales reports.
    When a sale is recorded, product stock is automatically reduced.
    """

    def __init__(self, db):
        self.db = db

    def record_sale(self, product_id, quantity_sold):
        """
        Record a sale for a product.
        Steps:
          1. Check if product exists
          2. Check if we have enough stock
          3. Insert sale record
          4. Reduce product quantity
        """
        cursor = self.db.get_cursor()
        if not cursor:
            return False

        # Step 1: Get product details
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            print(Fore.RED + f"[ERROR] Product ID {product_id} not found." + Style.RESET_ALL)
            return False

        # Step 2: Check stock availability
        if product["quantity"] < quantity_sold:
            print(Fore.RED + f"[ERROR] Not enough stock! Available: {product['quantity']}" + Style.RESET_ALL)
            return False

        # Calculate the total sale amount
        total = product["price"] * quantity_sold

        try:
            # Step 3: Insert into sales table
            sale_query = """
                INSERT INTO sales (product_id, quantity_sold, sale_price, total_amount)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sale_query, (product_id, quantity_sold, product["price"], total))

            # Step 4: Reduce stock from products table
            update_query = "UPDATE products SET quantity = quantity - %s WHERE id = %s"
            cursor.execute(update_query, (quantity_sold, product_id))

            self.db.commit()
            print(Fore.GREEN + f"\n✓ Sale recorded! {quantity_sold}x '{product['name']}' = ₹{total:.2f}" + Style.RESET_ALL)
            return True

        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not record sale: {e}" + Style.RESET_ALL)
            return False

    def get_sales_report(self):
        """
        Generate a full sales report by joining sales with products.
        Shows what was sold, when, and how much was earned.
        """
        cursor = self.db.get_cursor()
        if not cursor:
            return []

        query = """
            SELECT 
                s.id,
                p.name AS product,
                s.quantity_sold,
                s.sale_price,
                s.total_amount,
                DATE_FORMAT(s.sale_date, '%d-%m-%Y %H:%i') AS sold_on
            FROM sales s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.sale_date DESC
        """
        cursor.execute(query)
        return cursor.fetchall()

    def get_summary(self):
        """
        Return a quick stats summary:
        - Total revenue earned
        - Total number of sales transactions
        - Best-selling product
        """
        cursor = self.db.get_cursor()
        if not cursor:
            return {}

        # Total revenue and transaction count
        cursor.execute("SELECT SUM(total_amount) AS revenue, COUNT(*) AS transactions FROM sales")
        summary = cursor.fetchone()

        # Best-selling product (by quantity sold)
        cursor.execute("""
            SELECT p.name, SUM(s.quantity_sold) AS total_sold
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY s.product_id
            ORDER BY total_sold DESC
            LIMIT 1
        """)
        best = cursor.fetchone()

        return {
            "revenue": summary["revenue"] or 0,
            "transactions": summary["transactions"] or 0,
            "best_seller": best["name"] if best else "N/A",
            "best_qty": best["total_sold"] if best else 0
        }

    def display_report(self, sales):
        """Print the sales report as a table."""
        if not sales:
            print(Fore.YELLOW + "\nNo sales recorded yet." + Style.RESET_ALL)
            return

        table_data = [
            [s["id"], s["product"], s["quantity_sold"], f"₹{s['sale_price']:.2f}",
             f"₹{s['total_amount']:.2f}", s["sold_on"]]
            for s in sales
        ]
        headers = ["Sale ID", "Product", "Qty Sold", "Unit Price", "Total", "Date"]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
