-- ============================================================
-- Inventory Management System - Database Schema
-- Author: [Your Name]
-- Description: Schema for managing products, suppliers, and sales
-- ============================================================

-- Create and use the database
CREATE DATABASE IF NOT EXISTS inventory_db;
USE inventory_db;

-- ---------------------------------------------------------------
-- Table: suppliers
-- Stores supplier/vendor information
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------
-- Table: products
-- Stores product details including stock and pricing
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    quantity INT NOT NULL DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL,
    low_stock_threshold INT DEFAULT 10,   -- alert when stock falls below this
    supplier_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
);

-- ---------------------------------------------------------------
-- Table: sales
-- Tracks every sale transaction
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity_sold INT NOT NULL,
    sale_price DECIMAL(10, 2) NOT NULL,   -- price at time of sale
    total_amount DECIMAL(10, 2) NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------
-- Sample Data: Suppliers
-- ---------------------------------------------------------------
INSERT INTO suppliers (name, contact_person, phone, email, address) VALUES
('TechSupplies Ltd', 'Rahul Sharma', '9876543210', 'rahul@techsupplies.com', 'Mumbai, Maharashtra'),
('QuickStock Co.', 'Priya Mehta', '9123456780', 'priya@quickstock.com', 'Pune, Maharashtra'),
('GlobalGoods Inc.', 'Amit Verma', '9988776655', 'amit@globalgoods.com', 'Delhi, India');

-- ---------------------------------------------------------------
-- Sample Data: Products
-- ---------------------------------------------------------------
INSERT INTO products (name, category, quantity, price, low_stock_threshold, supplier_id) VALUES
('USB-C Cable', 'Electronics', 50, 299.00, 10, 1),
('Wireless Mouse', 'Electronics', 8, 799.00, 5, 1),
('A4 Notebook', 'Stationery', 200, 49.00, 20, 2),
('HDMI Cable', 'Electronics', 3, 399.00, 5, 1),
('Ballpoint Pen Box', 'Stationery', 150, 120.00, 15, 2),
('Laptop Stand', 'Accessories', 25, 1499.00, 5, 3),
('Webcam HD 1080p', 'Electronics', 12, 2499.00, 5, 1),
('Desk Lamp LED', 'Accessories', 6, 899.00, 5, 3);

-- ---------------------------------------------------------------
-- Sample Data: Sales
-- ---------------------------------------------------------------
INSERT INTO sales (product_id, quantity_sold, sale_price, total_amount) VALUES
(1, 5, 299.00, 1495.00),
(3, 10, 49.00, 490.00),
(6, 2, 1499.00, 2998.00),
(7, 3, 2499.00, 7497.00),
(2, 1, 799.00, 799.00),
(5, 20, 120.00, 2400.00);
