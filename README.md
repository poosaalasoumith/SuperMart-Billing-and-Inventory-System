# SuperMart Billing and Inventory Management System

A robust, console-based retail Point of Sale (POS) and inventory management system written in Python with MySQL database backend.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup & Configuration](#database-setup--configuration)
- [How to Run](#how-to-run)
- [Menu Options & Usage](#menu-options--usage)
- [Database Schema](#database-schema)
- [Security & Environment Variables](#security--environment-variables)
- [License](#license)

---

## Overview

**SuperMart Billing and Inventory Management System** is a streamlined retail management tool designed for small to medium supermarkets and grocery stores. It automates day-to-day retail operations, including product cataloging, category management, real-time stock tracking, point-of-sale checkout with automated receipt calculations (discounts and taxes), supplier purchase recording, customer management, and low-stock alerting.

---

## Key Features

- **Product & Category Management**:
  - Organize items by categories.
  - Track products with unique barcodes, unit cost price, selling price, current stock, and reorder levels.
  - Search products quickly by name or barcode.
- **Point of Sale (POS) Billing & Checkout**:
  - Fast barcode/product ID lookup for cart items.
  - Real-time stock validation during billing to prevent overselling.
  - Automated calculation of subtotal, custom discounts, tax percentages, and final payable amount.
  - Multiple payment method support (Cash, UPI, Card).
  - Transaction-safe atomic sales commit and itemized invoice logging.
- **Inventory & Purchase Receiving**:
  - Record supplier purchase orders and supplier invoices.
  - Automatically update current stock levels and update purchase costs upon stock arrival.
- **Stock Alert & Reporting**:
  - Instant low-stock warning report identifying items at or below reorder threshold.
  - Full sales history report with itemized billing breakdowns.
- **Customer & Supplier Directory**:
  - Maintain customer contact records.
  - Track vendors/suppliers with contact information for simplified purchase orders.
- **Automated Database Setup**:
  - Automatically creates the database and relational schema on the initial launch if not already present.

---

## Technologies Used

- **Language**: Python 3.10+
- **Database**: MySQL Server 8.0+
- **Database Driver**: `mysql-connector-python`
- **Environment Management**: `python-dotenv`

---

## Project Structure

```text
SuperMart_Billing_Inventory_System/
├── .env.example          # Environment variable template for MySQL configuration
├── .gitignore            # Git ignore file for secrets, cache, and virtual environments
├── main.py               # Main application entry point containing core logic & menu
├── README.md             # Project documentation
└── requirements.txt      # Python dependencies
```

---

## Prerequisites

Before running the application, ensure you have:

1. **Python 3.10 or higher**: [Download Python](https://www.python.org/downloads/)
2. **MySQL Server 8.0+**: Ensure MySQL service is installed and running locally.
3. **Git**: Installed for version control.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/poosaalasoumith/SuperMart-Billing-and-Inventory-System.git
   cd SuperMart-Billing-and-Inventory-System
   ```

2. **Create and activate a virtual environment** (recommended):
   - **Windows**:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Database Setup & Configuration

1. **Configure Environment Variables**:
   Copy `.env.example` to create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   *(On Windows Command Prompt / PowerShell: `copy .env.example .env`)*

2. **Edit `.env`** with your MySQL database credentials:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_PORT=3306
   DB_NAME=supermart_console_db
   ```

3. **Automatic Schema Initialization**:
   The application automatically provisions the MySQL database (`supermart_console_db`) and all required tables upon first launch. No manual SQL script execution is required!

---

## How to Run

Execute the main script from your terminal:

```bash
python main.py
```

---

## Menu Options & Usage

Upon launch, you will see the interactive console dashboard:

```text
==========================================================
              SUPERMART BILLING & INVENTORY               
==========================================================
1. Add category
2. Add product
3. View/search products
4. POS billing
5. Sales report
6. Add customer
7. Add supplier
8. Receive stock purchase
9. Low-stock report
0. Exit
Choice: 
```

### Quick Workflow Walkthrough

1. **Add Categories & Products**:
   - Select option `1` to define categories (e.g., *Beverages*, *Dairy*, *Snacks*).
   - Select option `2` to register products with prices, initial stock, and reorder threshold.
2. **Receive Stock from Suppliers**:
   - Add a supplier via option `7`.
   - Record inbound shipments via option `8` to increment stock counts.
3. **Conduct a Sale (POS Checkout)**:
   - Select option `4`.
   - Enter barcode or product ID and quantity for each item.
   - Enter `DONE` when cart is full.
   - Provide discount amount (if any) and tax percentage.
   - Select payment method (`Cash`, `UPI`, `Card`) to complete billing.
4. **Monitor Sales & Stock**:
   - Choose `5` to view all completed sales and revenue totals.
   - Choose `9` to review items running below safety stock levels.

---

## Database Schema

The relational database schema includes:

- **`categories`**: `id`, `name`
- **`products`**: `id`, `name`, `barcode`, `category_id`, `buy` price, `sell` price, `stock`, `reorder_level`
- **`customers`**: `id`, `name`, `phone`
- **`suppliers`**: `id`, `name`, `phone`
- **`sales`**: `id`, `customer_id`, `subtotal`, `tax`, `discount`, `total`, `method`, `sold_at`
- **`sale_items`**: `id`, `sale_id`, `product_id`, `qty`, `price`
- **`purchases`**: `id`, `supplier_id`, `invoice`, `total`, `created_at`
- **`purchase_items`**: `id`, `purchase_id`, `product_id`, `qty`, `cost`

---

## Security & Environment Variables

- Sensitive credentials (passwords, hosts, tokens) are isolated in `.env` and loaded via `python-dotenv`.
- The `.gitignore` file prevents `.env`, Python bytecode, and local database artifacts from ever being committed or exposed publicly.

---

## License

This project is licensed under the MIT License.
