import os
import mysql.connector

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "supermart_console_db")

DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "port": DB_PORT,
}

SCHEMA = [
    'CREATE TABLE IF NOT EXISTS categories(id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(80) UNIQUE)',
    'CREATE TABLE IF NOT EXISTS products(id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(120),barcode VARCHAR(80) UNIQUE,category_id INT,buy DECIMAL(12,2),sell DECIMAL(12,2),stock INT DEFAULT 0,reorder_level INT DEFAULT 5,FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL)',
    'CREATE TABLE IF NOT EXISTS customers(id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(120),phone VARCHAR(30))',
    'CREATE TABLE IF NOT EXISTS suppliers(id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(120),phone VARCHAR(30))',
    'CREATE TABLE IF NOT EXISTS sales(id INT AUTO_INCREMENT PRIMARY KEY,customer_id INT,subtotal DECIMAL(12,2),tax DECIMAL(12,2),discount DECIMAL(12,2),total DECIMAL(12,2),method VARCHAR(30),sold_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)',
    'CREATE TABLE IF NOT EXISTS sale_items(id INT AUTO_INCREMENT PRIMARY KEY,sale_id INT,product_id INT,qty INT,price DECIMAL(12,2),FOREIGN KEY(sale_id) REFERENCES sales(id),FOREIGN KEY(product_id) REFERENCES products(id))',
    'CREATE TABLE IF NOT EXISTS purchases(id INT AUTO_INCREMENT PRIMARY KEY,supplier_id INT,invoice VARCHAR(80),total DECIMAL(12,2),created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)',
    'CREATE TABLE IF NOT EXISTS purchase_items(id INT AUTO_INCREMENT PRIMARY KEY,purchase_id INT,product_id INT,qty INT,cost DECIMAL(12,2),FOREIGN KEY(purchase_id) REFERENCES purchases(id),FOREIGN KEY(product_id) REFERENCES products(id))'
]

def conn(database=True):
    c = DB_CONFIG.copy()
    if database:
        c["database"] = DB_NAME
    return mysql.connector.connect(**c)

def setup():
    c = conn(False)
    q = c.cursor()
    q.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
    q.close()
    c.close()
    c = conn()
    q = c.cursor()
    for s in SCHEMA:
        q.execute(s)
    c.commit()
    q.close()
    c.close()

def run(sql, args=(), fetch=False):
    c = conn()
    q = c.cursor(dictionary=True)
    try:
        q.execute(sql, args)
        out = q.fetchall() if fetch else q.lastrowid
        c.commit()
        return out
    finally:
        q.close()
        c.close()

def ask(s, default=None):
    x = input(f"{s}" + (f" [{default}]" if default is not None else "") + ": ").strip()
    return x or (str(default) if default is not None else "")

def num(s, integer=False, zero=False):
    while True:
        try:
            x = int(input(s + ": ")) if integer else float(input(s + ": "))
            if x > 0 or (zero and x == 0):
                return x
        except ValueError:
            pass
        print("Enter a valid positive number.")

def show(title, opts):
    print("\n" + "=" * 58 + "\n" + title.center(58) + "\n" + "=" * 58)
    for k, v in opts:
        print(k + ".", v)
    return input("Choice: ").strip()

def table(data):
    if not data:
        print("No records.")
        return
    keys = list(data[0])
    print(" | ".join(k.upper() for k in keys))
    print("-" * 100)
    for r in data:
        print(" | ".join(str(r[k]) for k in keys))

def pause():
    input("\nPress Enter...")

def money(x):
    return f"INR {float(x or 0):,.2f}"

def products():
    table(run("SELECT p.id,p.name,p.barcode,c.name category,p.buy,p.sell,p.stock,p.reorder_level FROM products p LEFT JOIN categories c ON c.id=p.category_id ORDER BY p.name", fetch=True))

def add_category():
    run("INSERT INTO categories(name) VALUES(%s)", (ask("Category name"),))

def add_product():
    cats = run("SELECT * FROM categories", fetch=True)
    table(cats)
    raw = ask("Category ID (blank none)")
    cid = int(raw) if raw else None
    run(
        "INSERT INTO products(name,barcode,category_id,buy,sell,stock,reorder_level) VALUES(%s,%s,%s,%s,%s,%s,%s)",
        (
            ask("Product name"),
            ask("Barcode (blank none)") or None,
            cid,
            num("Purchase price", zero=True),
            num("Selling price"),
            num("Opening stock", True, True),
            num("Reorder level", True, True),
        ),
    )

def checkout():
    cart = []
    while True:
        code = ask("Barcode or product ID (DONE to finish)")
        if code.upper() == "DONE":
            break
        p = run("SELECT * FROM products WHERE barcode=%s OR id=%s", (code, int(code) if code.isdigit() else -1), True)
        if not p:
            print("Product not found.")
            continue
        qty = num("Quantity", True)
        if qty > p[0]["stock"]:
            print("Insufficient stock.")
            continue
        cart.append((p[0], qty))
    if not cart:
        return
    sub = sum(float(p["sell"]) * q for p, q in cart)
    disc = num("Discount amount", zero=True)
    taxrate = num("Tax percent", zero=True)
    if disc > sub:
        print("Discount exceeds subtotal.")
        return
    tax = (sub - disc) * taxrate / 100
    total = sub - disc + tax
    print("Subtotal", money(sub), "Tax", money(tax), "Total", money(total))
    method = ask("Payment method Cash/UPI/Card")
    c = conn()
    cur = c.cursor()
    try:
        cur.execute("INSERT INTO sales(subtotal,tax,discount,total,method) VALUES(%s,%s,%s,%s,%s)", (sub, tax, disc, total, method))
        sid = cur.lastrowid
        for p, q in cart:
            cur.execute("UPDATE products SET stock=stock-%s WHERE id=%s AND stock>=%s", (q, p["id"], q))
            if cur.rowcount != 1:
                raise ValueError("Stock changed during sale.")
            cur.execute("INSERT INTO sale_items(sale_id,product_id,qty,price) VALUES(%s,%s,%s,%s)", (sid, p["id"], q, p["sell"]))
        c.commit()
        print("Sale completed. Bill ID", sid)
    except Exception:
        c.rollback()
        raise
    finally:
        cur.close()
        c.close()

def add_supplier():
    run("INSERT INTO suppliers(name,phone) VALUES(%s,%s)", (ask("Supplier name"), ask("Phone")))

def receive_stock():
    table(run("SELECT * FROM suppliers", fetch=True))
    sid = ask("Supplier ID (blank none)")
    sid = int(sid) if sid else None
    invoice = ask("Invoice number")
    items = []
    while True:
        products()
        raw = ask("Product ID (0 finish)")
        if raw == "0":
            break
        p = run("SELECT * FROM products WHERE id=%s", (int(raw),), True)
        if not p:
            continue
        items.append((p[0], num("Quantity", True), num("Unit cost", zero=True)))
    if not items:
        return
    total = sum(q * cost for p, q, cost in items)
    c = conn()
    cur = c.cursor()
    try:
        cur.execute("INSERT INTO purchases(supplier_id,invoice,total) VALUES(%s,%s,%s)", (sid, invoice, total))
        pid = cur.lastrowid
        for p, q, cost in items:
            cur.execute("INSERT INTO purchase_items(purchase_id,product_id,qty,cost) VALUES(%s,%s,%s,%s)", (pid, p["id"], q, cost))
            cur.execute("UPDATE products SET stock=stock+%s,buy=%s WHERE id=%s", (q, cost, p["id"]))
        c.commit()
        print("Stock received. Purchase ID", pid)
    except Exception:
        c.rollback()
        raise
    finally:
        cur.close()
        c.close()

def main():
    setup()
    while True:
        c = show(
            "SUPERMART BILLING & INVENTORY",
            [
                ("1", "Add category"),
                ("2", "Add product"),
                ("3", "View/search products"),
                ("4", "POS billing"),
                ("5", "Sales report"),
                ("6", "Add customer"),
                ("7", "Add supplier"),
                ("8", "Receive stock purchase"),
                ("9", "Low-stock report"),
                ("0", "Exit"),
            ],
        )
        try:
            if c == "0":
                break
            elif c == "1":
                add_category()
            elif c == "2":
                add_product()
            elif c == "3":
                term = ask("Search term (blank all)")
                table(run("SELECT id,name,barcode,sell,stock FROM products WHERE name LIKE %s OR barcode LIKE %s", ("%" + term + "%", "%" + term + "%"), True))
            elif c == "4":
                checkout()
            elif c == "5":
                table(run("SELECT id,subtotal,tax,discount,total,method,sold_at FROM sales ORDER BY id DESC", fetch=True))
            elif c == "6":
                run("INSERT INTO customers(name,phone) VALUES(%s,%s)", (ask("Customer name"), ask("Phone")))
            elif c == "7":
                add_supplier()
            elif c == "8":
                receive_stock()
            elif c == "9":
                table(run("SELECT id,name,stock,reorder_level FROM products WHERE stock<=reorder_level", fetch=True))
            else:
                print("Invalid choice.")
        except Exception as e:
            print("Error:", e)
        pause()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Startup/MySQL error:", e, "Check DB_CONFIG and MySQL service.")
