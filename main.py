import sqlite3
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator, field_validator
from typing import List, Optional

# Initialize FastAPI app
app = FastAPI()


# Database connection
def get_db():
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn


# Database initialization
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create Company Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS company (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        address TEXT,
        phone TEXT,
        city TEXT,
        state TEXT,
        zipcode TEXT
    )
    ''')

    # Create Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        item_name TEXT NOT NULL,
        rate REAL NOT NULL
    )
    ''')

    # Create Bills Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        date TEXT NOT NULL,
        sl_number INTEGER NOT NULL,
        company_id INTEGER NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (company_id) REFERENCES company(id)
    )
    ''')

    # Create Bill Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bill_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        bill_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY (bill_id) REFERENCES bills(id),
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
    ''')

    conn.commit()
    conn.close()


# Initialize database tables
init_db()


# Pydantic models
class Company(BaseModel):
    name: str
    address: str
    phone: str
    city: str
    state: str
    zipcode: str


class Item(BaseModel):
    item_name: str
    rate: float


class BillItem(BaseModel):
    quantity: int
    item_id: int
    rate: float


class Bill(BaseModel):
    date: str  # Accepting date as a string to be parsed
    sl_number: int
    company_id: int
    bill_items: List[BillItem]

    @field_validator('date')
    def validate_date(cls, value):
        try:
            # Attempt to parse the date; format assumed as YYYY-MM-DD for this example
            return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("Incorrect date format. Expected YYYY-MM-DD.")


# API Endpoints

@app.post("/companies/")
def create_company(company: Company):
    conn = get_db()
    cursor = conn.cursor()
    company_uuid = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO company (uuid, name, address, phone, city, state, zipcode)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (company_uuid, company.name, company.address, company.phone, company.city, company.state, company.zipcode))
    conn.commit()
    conn.close()
    return {"company_uuid": company_uuid, "message": "Company created successfully"}


@app.post("/items/")
def create_item(item: Item):
    conn = get_db()
    cursor = conn.cursor()
    item_uuid = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO items (uuid, item_name, rate)
        VALUES (?, ?, ?)
    ''', (item_uuid, item.item_name, item.rate))
    conn.commit()
    conn.close()
    return {"item_uuid": item_uuid, "message": "Item created successfully"}


@app.post("/bills/")
def create_bill(bill: Bill):
    conn = get_db()
    cursor = conn.cursor()

    # Parse and verify the date
    try:
        date = datetime.strptime(bill.date, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    # Calculate total
    total = sum(item.quantity * item.rate for item in bill.bill_items)

    # Insert the bill
    bill_uuid = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO bills (uuid, date, sl_number, company_id, total)
        VALUES (?, ?, ?, ?, ?)
    ''', (bill_uuid, date, bill.sl_number, bill.company_id, total))
    bill_id = cursor.lastrowid

    # Insert bill items
    for item in bill.bill_items:
        item_uuid = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO bill_items (uuid, bill_id, quantity, item_id, amount)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_uuid, bill_id, item.quantity, item.item_id, item.quantity * item.rate))

    conn.commit()
    conn.close()
    return {"bill_uuid": bill_uuid, "message": "Bill created successfully"}


@app.get("/bills/{bill_id}")
def get_bill(bill_id: int):
    conn = get_db()
    cursor = conn.cursor()

    # Fetch bill
    cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
    bill = cursor.fetchone()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # Fetch bill items
    cursor.execute("SELECT * FROM bill_items WHERE bill_id = ?", (bill_id,))
    bill_items = cursor.fetchall()

    conn.close()
    return {
        "bill": dict(bill),
        "bill_items": [dict(item) for item in bill_items]
    }

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor()

    # Query for the item with the specified item_id
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    conn.close()

    # If item not found, raise an HTTP 404 error
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Convert item data to dictionary and return
    return {
        "id": item["id"],
        "item_name": item["item_name"],
        "rate": item["rate"]
    }
