"""
main.py
-------
Entry point for the Inventory Management System.
This file contains the CLI menu loop and all user interaction.

Run this file to start the application:
    python main.py

The program keeps running in a loop until the user chooses to exit.
"""

from colorama import Fore, Back, Style, init
from database import Database
from models import ProductManager, SupplierManager, SalesManager

# Initialize colorama (needed for Windows color support)
init(autoreset=True)


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def print_header(title):
    """Print a styled section header."""
    print("\n" + "=" * 55)
    print(Fore.CYAN + Style.BRIGHT + f"  {title}")
    print("=" * 55 + Style.RESET_ALL)


def get_int_input(prompt, min_val=None, max_val=None):
    """
    Keep asking for input until the user gives a valid integer.
    Useful for menu choices and numeric fields.
    """
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(Fore.YELLOW + f"  Value must be at least {min_val}." + Style.RESET_ALL)
                continue
            if max_val is not None and value > max_val:
                print(Fore.YELLOW + f"  Value must be at most {max_val}." + Style.RESET_ALL)
                continue
            return value
        except ValueError:
            print(Fore.YELLOW + "  Please enter a valid number." + Style.RESET_ALL)


def get_float_input(prompt, min_val=0.0):
    """Keep asking for input until the user gives a valid float (decimal number)."""
    while True:
        try:
            value = float(input(prompt))
            if value < min_val:
                print(Fore.YELLOW + f"  Value must be at least {min_val}." + Style.RESET_ALL)
                continue
            return value
        except ValueError:
            print(Fore.YELLOW + "  Please enter a valid number." + Style.RESET_ALL)


def confirm_action(prompt="Are you sure? (y/n): "):
    """Ask the user to confirm a destructive action."""
    return input(prompt).strip().lower() == 'y'


# ================================================================
# PRODUCT MENU FUNCTIONS
# ================================================================

def menu_add_product(pm, sm):
    """Collect product details from user and add to database."""
    print_header("ADD NEW PRODUCT")

    name = input("  Product name: ").strip()
    if not name:
        print(Fore.RED + "  Name cannot be empty." + Style.RESET_ALL)
        return

    category = input("  Category (e.g., Electronics, Stationery): ").strip()
    quantity = get_int_input("  Initial quantity: ", min_val=0)
    price = get_float_input("  Price (₹): ", min_val=0.01)
    threshold = get_int_input("  Low stock alert threshold: ", min_val=1)

    # Show suppliers so user can pick one
    suppliers = sm.get_all_suppliers()
    supplier_id = None
    if suppliers:
        sm.display_suppliers(suppliers)
        choice = input("\n  Enter Supplier ID (or press Enter to skip): ").strip()
        if choice.isdigit():
            supplier_id = int(choice)

    pm.add_product(name, category, quantity, price, threshold, supplier_id)


def menu_view_products(pm):
    """Display all products."""
    print_header("ALL PRODUCTS")
    products = pm.get_all_products()
    pm.display_products(products)


def menu_search_products(pm):
    """Search products by keyword."""
    print_header("SEARCH PRODUCTS")
    keyword = input("  Enter search keyword: ").strip()
    if not keyword:
        print(Fore.YELLOW + "  Keyword cannot be empty." + Style.RESET_ALL)
        return
    results = pm.search_products(keyword)
    pm.display_products(results)
    if results:
        print(f"\n  Found {len(results)} result(s) for '{keyword}'")


def menu_update_product(pm):
    """Update an existing product's details."""
    print_header("UPDATE PRODUCT")
    
    # First show all products so user knows which ID to pick
    products = pm.get_all_products()
    pm.display_products(products)
    if not products:
        return

    product_id = get_int_input("\n  Enter Product ID to update: ", min_val=1)
    product = pm.get_product_by_id(product_id)

    if not product:
        print(Fore.RED + f"  No product found with ID {product_id}." + Style.RESET_ALL)
        return

    print(f"\n  Updating: {product['name']} (press Enter to keep current value)")

    # If user presses Enter without typing, keep the existing value
    name = input(f"  Name [{product['name']}]: ").strip() or product["name"]
    category = input(f"  Category [{product['category']}]: ").strip() or product["category"]
    
    qty_input = input(f"  Quantity [{product['quantity']}]: ").strip()
    quantity = int(qty_input) if qty_input.isdigit() else product["quantity"]

    price_input = input(f"  Price [₹{product['price']}]: ").strip()
    price = float(price_input) if price_input else product["price"]

    thresh_input = input(f"  Low stock threshold [{product['low_stock_threshold']}]: ").strip()
    threshold = int(thresh_input) if thresh_input.isdigit() else product["low_stock_threshold"]

    pm.update_product(product_id, name, category, quantity, price, threshold)


def menu_delete_product(pm):
    """Delete a product after confirmation."""
    print_header("DELETE PRODUCT")
    
    products = pm.get_all_products()
    pm.display_products(products)
    if not products:
        return

    product_id = get_int_input("\n  Enter Product ID to delete: ", min_val=1)
    product = pm.get_product_by_id(product_id)

    if not product:
        print(Fore.RED + f"  No product found with ID {product_id}." + Style.RESET_ALL)
        return

    print(Fore.YELLOW + f"\n  You are about to delete: '{product['name']}'" + Style.RESET_ALL)
    if confirm_action("  Confirm delete? (y/n): "):
        pm.delete_product(product_id)
    else:
        print("  Deletion cancelled.")


def menu_low_stock_alert(pm):
    """Show all products with low stock."""
    print_header("LOW STOCK ALERT")
    low_stock = pm.get_low_stock_products()
    pm.display_low_stock(low_stock)


# ================================================================
# SUPPLIER MENU FUNCTIONS
# ================================================================

def menu_supplier(sm):
    """Sub-menu for supplier management."""
    while True:
        print_header("SUPPLIER MANAGEMENT")
        print("  1. View all suppliers")
        print("  2. Add new supplier")
        print("  3. Delete supplier")
        print("  0. Back to main menu")

        choice = get_int_input("\n  Your choice: ", min_val=0, max_val=3)

        if choice == 1:
            suppliers = sm.get_all_suppliers()
            sm.display_suppliers(suppliers)

        elif choice == 2:
            print_header("ADD SUPPLIER")
            name = input("  Company name: ").strip()
            contact = input("  Contact person: ").strip()
            phone = input("  Phone number: ").strip()
            email = input("  Email address: ").strip()
            address = input("  Address: ").strip()
            sm.add_supplier(name, contact, phone, email, address)

        elif choice == 3:
            suppliers = sm.get_all_suppliers()
            sm.display_suppliers(suppliers)
            if suppliers:
                sid = get_int_input("\n  Enter Supplier ID to delete: ", min_val=1)
                if confirm_action("  Confirm delete? (y/n): "):
                    sm.delete_supplier(sid)

        elif choice == 0:
            break

        input("\n  Press Enter to continue...")


# ================================================================
# SALES MENU FUNCTIONS
# ================================================================

def menu_sales(sales_mgr, pm):
    """Sub-menu for sales management."""
    while True:
        print_header("SALES MANAGEMENT")
        print("  1. Record a sale")
        print("  2. View sales report")
        print("  3. View summary statistics")
        print("  0. Back to main menu")

        choice = get_int_input("\n  Your choice: ", min_val=0, max_val=3)

        if choice == 1:
            print_header("RECORD SALE")
            products = pm.get_all_products()
            pm.display_products(products)
            if products:
                pid = get_int_input("\n  Enter Product ID: ", min_val=1)
                qty = get_int_input("  Quantity sold: ", min_val=1)
                sales_mgr.record_sale(pid, qty)

        elif choice == 2:
            print_header("SALES REPORT")
            sales = sales_mgr.get_sales_report()
            sales_mgr.display_report(sales)

        elif choice == 3:
            print_header("SUMMARY STATISTICS")
            summary = sales_mgr.get_summary()
            print(f"\n  {'Total Revenue:':<25} ₹{summary['revenue']:.2f}")
            print(f"  {'Total Transactions:':<25} {summary['transactions']}")
            print(f"  {'Best-Selling Product:':<25} {summary['best_seller']} ({summary['best_qty']} units)")

        elif choice == 0:
            break

        input("\n  Press Enter to continue...")


# ================================================================
# MAIN MENU
# ================================================================

def main_menu():
    """Display the main menu and return user's choice."""
    print_header("INVENTORY MANAGEMENT SYSTEM")
    print("  1. View all products")
    print("  2. Add new product")
    print("  3. Update product")
    print("  4. Delete product")
    print("  5. Search products")
    print("  6. Low stock alerts")
    print("  7. Supplier management")
    print("  8. Sales management")
    print("  0. Exit")
    return get_int_input("\n  Your choice: ", min_val=0, max_val=8)


# ================================================================
# ENTRY POINT
# ================================================================

def main():
    """
    Main function — sets up the database connection and
    runs the application loop.
    """
    print(Fore.CYAN + Style.BRIGHT)
    print("=" * 55)
    print("   INVENTORY MANAGEMENT SYSTEM")
    print("   Built with Python + MySQL")
    print("=" * 55)
    print(Style.RESET_ALL)

    # --- Connect to database ---
    db = Database(
        host="localhost",
        user="root",       # ← change this
        password="",       # ← change this
        database="inventory_db"
    )

    if not db.connect():
        print(Fore.RED + "\nFailed to connect to database. Exiting." + Style.RESET_ALL)
        return

    print(Fore.GREEN + "  ✓ Connected to database successfully!\n" + Style.RESET_ALL)

    # --- Initialize managers ---
    product_manager = ProductManager(db)
    supplier_manager = SupplierManager(db)
    sales_manager = SalesManager(db)

    # --- Main application loop ---
    while True:
        choice = main_menu()

        if choice == 1:
            menu_view_products(product_manager)

        elif choice == 2:
            menu_add_product(product_manager, supplier_manager)

        elif choice == 3:
            menu_update_product(product_manager)

        elif choice == 4:
            menu_delete_product(product_manager)

        elif choice == 5:
            menu_search_products(product_manager)

        elif choice == 6:
            menu_low_stock_alert(product_manager)

        elif choice == 7:
            menu_supplier(supplier_manager)

        elif choice == 8:
            menu_sales(sales_manager, product_manager)

        elif choice == 0:
            print(Fore.CYAN + "\n  Thanks for using Inventory Manager. Goodbye!\n" + Style.RESET_ALL)
            db.close()
            break

        # Pause after each action so user can read the output
        if choice != 0:
            input("\n  Press Enter to continue...")


# Run main() only when this script is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    main()
